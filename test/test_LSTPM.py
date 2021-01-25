import os
import torch
from trafficdl.config import ConfigParser
from trafficdl.data import get_dataset
from trafficdl.utils import get_executor, get_model
from trafficdl.utils.dataset import parseCoordinate
from geopy import distance
import numpy as np
import torch.nn.functional as F

config = ConfigParser('traj_loc_pred', 'LSTPM', 'foursquare_tky', None, {"history_type": 'cut_off'})
dataset = get_dataset(config)
train_data, valid_data, test_data = dataset.get_data()
data_feature = dataset.get_data_feature()
batch = valid_data.__iter__().__next__()
model = get_model(config, data_feature)
self = model.to(config['device'])
batch.to_tensor(config['device'])
logp_seq = self.forward(batch, False)
executor = get_executor(config, model)

'''
item_vectors = batch['current_loc']
batch_size = item_vectors.size()[0]
sequence_size = item_vectors.size()[1]
items = self.item_emb(item_vectors)
item_vectors = item_vectors.tolist()
x = items # batch_size * sequence * embedding
x = x.transpose(0, 1)
h1 = torch.zeros(1, batch_size, self.hidden_size).to(self.device)
c1 = torch.zeros(1, batch_size, self.hidden_size).to(self.device)
out, (h1, c1) = self.lstmcell(x, (h1, c1))
out = out.transpose(0, 1)#batch_size * sequence_length * embedding_dim
x1 = items
# ###########################################################
user_batch = np.array(batch['uid'].cpu())
y_list = []
out_hie = []
ii = 0
    ##########################################
current_session_input_dilated_rnn_index = self._create_dilated_rnn_input(batch['current_loc'][ii].tolist())
hiddens_current = x1[ii]
dilated_lstm_outs_h = []
dilated_lstm_outs_c = []
for index_dilated in range(len(current_session_input_dilated_rnn_index)):
    index_dilated_explicit = current_session_input_dilated_rnn_index[index_dilated]
    hidden_current = hiddens_current[index_dilated].unsqueeze(0)
    if index_dilated == 0:
        h = torch.zeros(1, self.hidden_size).to(self.device)
        c = torch.zeros(1, self.hidden_size).to(self.device)
        (h, c) = self.dilated_rnn(hidden_current, (h, c))
        dilated_lstm_outs_h.append(h)
        dilated_lstm_outs_c.append(c)
    else:
        (h, c) = self.dilated_rnn(hidden_current, (dilated_lstm_outs_h[index_dilated_explicit], dilated_lstm_outs_c[index_dilated_explicit]))
        dilated_lstm_outs_h.append(h)
        dilated_lstm_outs_c.append(c)

dilated_lstm_outs_h.append(hiddens_current[len(current_session_input_dilated_rnn_index):])
dilated_out = torch.cat(dilated_lstm_outs_h, dim = 0).unsqueeze(0)
out_hie.append(dilated_out)
user_id_current = user_batch[ii]
current_session_timid = batch['current_tim'][ii].tolist()[:-1]
current_session_poiid = item_vectors[ii][:len(current_session_timid)]
current_session_embed = out[ii] # sequence_len * embedding_size
current_session_mask = self._pad_batch_of_lists_masks(batch['current_loc'][ii].cpu()).unsqueeze(1) # FloatTensor sequence_len * 1
# mask_batch_ix_non_local[ii].unsqueeze(1)
sequence_length = int(sum(np.array(current_session_mask.cpu())))
current_session_represent_list = []
if is_train:
    for iii in range(sequence_length-1):
        current_session_represent = torch.sum(current_session_embed * current_session_mask, dim=0).unsqueeze(0)/sum(current_session_mask)
        current_session_represent_list.append(current_session_represent)
else:
    for iii in range(sequence_length-1):
        current_session_represent_rep_item = current_session_embed[0:iii+1]
        current_session_represent_rep_item = torch.sum(current_session_represent_rep_item, dim = 0).unsqueeze(0)/(iii + 1)
        current_session_represent_list.append(current_session_represent_rep_item
current_session_represent = torch.cat(current_session_represent_list, dim = 0)
list_for_sessions = []
list_for_avg_distance = []
h2 = torch.zeros(1, 1, self.hidden_size).to(self.device)###whole sequence
c2 = torch.zeros(1, 1, self.hidden_size).to(self.device)
# 处理历史轨迹
for jj in range(len(batch['history_loc'][ii])):
    sequence = batch['history_loc'][ii][jj]
    sequence_emb = self.item_emb(sequence).unsqueeze(1) # sequence_len * 1 * embedding_size 
    sequence = sequence.tolist()
    sequence_emb, (h2, c2) = self.lstmcell_history(sequence_emb, (h2, c2))
    sequence_tim_id = batch['history_tim'][ii][jj].tolist()
    jaccard_sim_row = torch.FloatTensor(self.tim_sim_matrix[current_session_timid]).to(self.device) # 相当于自己做了一个 tim 的表征
    jaccard_sim_expicit = jaccard_sim_row[:,sequence_tim_id]
    # 使用 profile 计算局部距离矩阵
    distance_matrix = []
    for origin in current_session_poiid:
        lon_cur, lat_cur = parseCoordinate(self.poi_profile.iloc[origin]['coordinates'])
        distance_row = []
        for target in sequence:
            lon, lat = parseCoordinate(self.poi_profile.iloc[target]['coordinates'])
            distance_row.append(distance.distance((lat_cur, lon_cur), (lat, lon)).kilometers)
        distance_matrix.append(distance_row)
    distance_row_expicit = torch.FloatTensor(distance_matrix).to(self.device)
    # distance_row = self.poi_distance_matrix[current_session_poiid]
    # distance_row_expicit = torch.FloatTensor(distance_row[:,sequence]).to(self.device)
    distance_row_expicit_avg = torch.mean(distance_row_expicit, dim = 1)
    jaccard_sim_expicit_last = F.softmax(jaccard_sim_expicit, dim = 1)
    hidden_sequence_for_current1 = torch.mm(jaccard_sim_expicit_last, sequence_emb.squeeze(1))
    hidden_sequence_for_current =  hidden_sequence_for_current1
    list_for_sessions.append(hidden_sequence_for_current.unsqueeze(0))
    list_for_avg_distance.append(distance_row_expicit_avg.unsqueeze(0))
avg_distance = torch.cat(list_for_avg_distance, dim = 0).transpose(0,1)
sessions_represent = torch.cat(list_for_sessions, dim=0).transpose(0,1) ##current_items * history_session_length * embedding_size
current_session_represent = current_session_represent.unsqueeze(2) ### current_items * embedding_size * 1
sims = F.softmax(sessions_represent.bmm(current_session_represent).squeeze(2), dim = 1).unsqueeze(1) ##==> current_items * 1 * history_session_length
#out_y_current = sims.bmm(sessions_represent).squeeze(1)
out_y_current =torch.selu(self.linear1(sims.bmm(sessions_represent).squeeze(1)))
##############layer_2
#layer_2_current = (lambda*out_y_current + (1-lambda)*current_session_embed[:sequence_length-1]).unsqueeze(2) #lambda from [0.1-0.9] better performance
# layer_2_current = (out_y_current + current_session_embed[:sequence_length-1]).unsqueeze(2)##==>current_items * embedding_size * 1
layer_2_current = (0.5 *out_y_current + 0.5 * current_session_embed[:sequence_length - 1]).unsqueeze(2)
layer_2_sims =  F.softmax(sessions_represent.bmm(layer_2_current).squeeze(2) * 1.0/avg_distance, dim = 1).unsqueeze(1)##==>>current_items * 1 * history_session_length
out_layer_2 = layer_2_sims.bmm(sessions_represent).squeeze(1)
# out_y_current_padd = torch.FloatTensor(sequence_size - sequence_length + 1, self.emb_size).zero_().to(self.device) # TODO: 感觉他这个是把 target 当成 current 的最后一个点了，有点问题
# out_layer_2_list = []
# out_layer_2_list.append(out_layer_2)
# out_layer_2_list.append(out_y_current_padd)
# out_layer_2 = torch.cat(out_layer_2_list,dim = 0).unsqueeze(0)
out_layer_2 = out_layer_2.unsqueeze(0)
y_list.append(out_layer_2)
y = torch.selu(torch.cat(y_list,dim=0))
out_hie = F.selu(torch.cat(out_hie, dim = 0))
out = F.selu(out)
out = (out + out_hie) * 0.5
out_put_emb_v1 = torch.cat([y, out], dim=2)
output_ln = self.linear(out_put_emb_v1)
output = F.log_softmax(output_ln, dim=-1)
'''
