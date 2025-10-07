# Usage

This guide provides instructions for using the components of the Model Lab, including data labeling, model training, and evaluation.

## Data Labeling

To prepare a new dataset for training, start Label Studio with the following command:

```bash
uv run label-studio start
```

This will launch the Label Studio web interface for data annotation and labeling.
## Model Training

1. Configure the training parameters in `model-lab/model-training.py`
2. Start the training process:

```bash
uv run model-lab/model-training.py
```

### Ultralytics Settings Reference

The following `settings.json` configuration is used for Ultralytics:

```json
{
  "settings_version": "0.0.6",
  "datasets_dir": "/home/xnorspx/Projects/Stream2Prompt/model-lab/ds",
  "weights_dir": "/home/xnorspx/Projects/Stream2Prompt/model-lab/weights",
  "runs_dir": "/home/xnorspx/Projects/Stream2Prompt/model-lab/runs",
  "uuid": "5bcc1cf32ada676916ec735cd4e216c62ff1e97244777357720c2ca28a7b7314",
  "sync": true,
  "api_key": "",
  "openai_api_key": "",
  "clearml": true,
  "comet": true,
  "dvc": true,
  "hub": true,
  "mlflow": true,
  "neptune": true,
  "raytune": true,
  "tensorboard": false,
  "wandb": false,
  "vscode_msg": true,
  "openvino_msg": false
}
```
## Model Evaluation

To test and evaluate your trained models, run the evaluation script and select the model you want to test:

```bash
uv run model-lab/model-eval.py
```

The script will prompt you to choose from available trained models for evaluation.
