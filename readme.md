![](https://bigscity-libcity-docs.readthedocs.io/en/latest/_images/logo.png)

------

# LibCity（阡陌）

[HomePage](https://lib-city.com/)|[Docs](https://bigscity-libcity-docs.readthedocs.io/en/latest/index.html)|[Datasets](https://github.com/LibCity/Bigscity-LibCity-Datasets)|[Paper List](https://github.com/LibCity/Bigscity-LibCity-Paper) |[中文版](https://github.com/LibCity/Bigscity-LibCity/blob/master/readme_zh.md)

LibCity is a unified, comprehensive, and extensible library, which provides researchers with a credible experimental tool and a convenient development framework in the traffic prediction field. Our library is implemented based on PyTorch and includes all the necessary steps or components related to traffic prediction into a systematic pipeline, allowing researchers to conduct comprehensive experiments. Our library will contribute to the standardization and reproducibility in the field of traffic prediction.

LibCity currently supports the following tasks:

* Traffic State Prediction
  * Traffic Flow Prediction
  * Traffic Speed Prediction
  * On-Demand Service Prediction
* Trajectory Next-Location Prediction

## Features

* **Unified**: LibCity builds a systematic pipeline to implement, use and evaluate traffic prediction models in a unified platform. We design basic spatial-temporal data storage, unified model instantiation interfaces, and standardized evaluation procedure.

* **Comprehensive**: 42 models covering four traffic prediction tasks have been reproduced to form a comprehensive model warehouse. Meanwhile, LibCity collects 29 commonly used datasets of different sources and implements a series of commonly used evaluation metrics and strategies for performance evaluation. 

* **Extensible**: LibCity enables a modular design of different components, allowing users to flexibly insert customized components into the library. Therefore, new researchers can easily develop new models with the support of LibCity.

## Overall Framework

![](https://bigscity-libcity-docs.readthedocs.io/en/latest/_images/framework.png)

* **Configuration Module**: Responsible for managing all the parameters involved in the framework.
* **Data Module**: Responsible for loading datasets and data preprocessing operations.
* **Model Module**: Responsible for initializing the reproduced baseline model or custom model.
* **Evaluation Module**: Responsible for evaluating model prediction results through multiple indicators.
* **Execution Module**: Responsible for model training and prediction.

## Installation

LibCity can only be installed from source code.

Please execute the following command to get the source code.

```shell
git clone https://github.com/LibCity/Bigscity-LibCity
cd Bigscity-LibCity
```

More details about environment configuration is represented in [Docs](https://bigscity-libcity-docs.readthedocs.io/en/latest/get_started/install.html).

## Quick-Start

Before run models in LibCity, please make sure you download at least one dataset and put it in directory `./raw_data/`. The dataset link is [BaiduDisk with code 1231](https://pan.baidu.com/s/1qEfcXBO-QwZfiT0G3IYMpQ) or [Google Drive](https://drive.google.com/drive/folders/1g5v2Gq1tkOq8XO0HDCZ9nOTtRpB6-gPe?usp=sharing).

The script `run_model.py` is used for training and evaluating a single model in LibCity. When run the `run_model.py`, you must specify the following three parameters, namely **task**, **dataset** and **model**.  

For example:

```sh
python run_model.py --task traffic_state_pred --model GRU --dataset METR_LA
```

This script will run the GRU model on the METR_LA dataset for traffic state prediction task under the default configuration. 

More details is represented in [Docs](https://bigscity-libcity-docs.readthedocs.io/en/latest/get_started/quick_start.html).

## Contribution

The LibCity is mainly developed and maintained by Beihang Interest Group on SmartCity ([BIGSCITY](https://www.bigcity.ai/)). The core developers of this library are [@aptx1231](https://github.com/aptx1231) and [@WenMellors](https://github.com/WenMellors). 

Several co-developers have also participated in the reproduction of  the model, the list of contributions of which is presented in the [reproduction contribution list](./contribution_list.md).

If you encounter a bug or have any suggestion, please contact us by [raising an issue](https://github.com/LibCity/Bigscity-LibCity/issues).

## License

LibCity uses [Apache License 2.0](https://github.com/LibCity/Bigscity-LibCity/blob/master/LICENSE.txt).

