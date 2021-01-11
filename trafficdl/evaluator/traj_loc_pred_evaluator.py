import numpy as np
import os
import json
import time

from trafficdl.evaluator.abstract_evaluator import AbstractEvaluator
from trafficdl.evaluator.eval_funcs import top_k
allowed_metrics = ['Precision', 'Recall', 'F1', 'MRR', 'MAP', 'NDCG']

class TrajLocPredEvaluator(AbstractEvaluator):

    def __init__(self, config):
        self.metrics = config['metrics'] # 评估指标, 是一个 list
        self.config = config
        self.topk = config['topk']
        self.result = {}
        self.intermediate_result = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self._check_config()

    def _check_config(self):
        if not isinstance(self.metrics, list):
            raise TypeError('Evaluator type is not list')
        for i in self.metrics:
            if i not in allowed_metrics:
                raise ValueError('the metric is not allowed in TrajLocPredEvaluator')
    
    def collect(self, batch):
        '''
        Args:
            batch (dict): contains three keys: uid, loc_true, and loc_pred.
            uid (list): 来自于 batch 中的 uid，通过索引可以确定 loc_true 与 loc_pred 中每一行（元素）是哪个用户的一次输入。
            loc_true (list): 期望地点(target)，来自于 batch 中的 target
            loc_pred (matrix): 实际上模型的输出，batch_size * output_dim. 
        '''
        if not isinstance(batch, dict):
            raise TypeError('evaluator.collect input is not a dict of user')
        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], self.topk)
        total = len(batch['loc_true'])
        self.intermediate_result['total'] += total
        self.intermediate_result['hit'] += hit
        self.intermediate_result['rank'] += rank
        self.intermediate_result['dcg'] += dcg
            

    def evaluate(self):
        if 'Precision' in self.metrics or 'F1' in self.metrics:
            self.result['Precision@{}'.format(self.topk)] = self.intermediate_result['hit'] / (self.intermediate_result['total'] * self.topk)
        # recall is used to valid in the trainning, so must exit
        self.result['Recall@{}'.format(self.topk)] = self.intermediate_result['hit'] / self.intermediate_result['total']
        if 'F1' in self.metrics:
            self.result['F1@{}'.format(self.topk)] = (2 * self.result['Precision@{}'.format(self.topk)] * self.result['Recall@{}'.format(self.topk)]) / (self.result['Precision@{}'.format(self.topk)] + self.result['Recall@{}'.format(self.topk)])
        if 'MRR' in self.metrics:
            self.result['MRR@{}'.format(self.topk)] = self.intermediate_result['rank'] / self.intermediate_result['total']
        if 'MAP' in self.metrics:
            self.result['MAP@{}'.format(self.topk)] = self.intermediate_result['rank'] / self.intermediate_result['total']
        if 'NDCG' in self.metrics:
            self.result['NDCG@{}'.format(self.topk)] = self.intermediate_result['dcg'] / self.intermediate_result['total']
        return self.result
    
    def save_result(self, save_path, filename=None):
        self.evaluate()
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        if filename == None:
            # 使用时间戳
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))
        print('evaluate result is ', json.dumps(self.result, indent=1))
        with open(os.path.join(save_path, '{}.json'.format(filename)), 'w') as f:
            json.dump(self.result, f)

    def clear(self):
        self.result = {}
        self.intermediate_result = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
