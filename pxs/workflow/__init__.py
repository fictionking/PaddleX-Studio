from typing import Any, Dict, Optional, Union
from paddlex.inference.utils.pp_option import PaddlePredictorOption
from paddlex.inference.utils.hpi import HPIConfig
from .pipeline import WorkflowPipeline

def create_workflow(
    config: Dict[str, Any],
    device: Optional[str] = None,
    pp_option: Optional[PaddlePredictorOption] = None,
    use_hpip: Optional[bool] = None,
    hpi_config: Optional[Union[Dict[str, Any], HPIConfig]] = None,
    *args: Any,
    **kwargs: Any,
) -> WorkflowPipeline:
    """
    Create a pipeline instance based on the provided parameters.


    Args:
        config (Optional[Dict[str, Any]], optional): The pipeline configuration.
            Defaults to None.
        device (Optional[str], optional): The device to run the pipeline on.
            Defaults to None.
        pp_option (Optional[PaddlePredictorOption], optional): The options for
            the PaddlePredictor. Defaults to None.
        use_hpip (Optional[bool], optional): Whether to use the high-performance
            inference plugin (HPIP). If set to None, the setting from the
            configuration file or `config` will be used. Defaults to None.
        hpi_config (Optional[Union[Dict[str, Any], HPIConfig]], optional): The
            high-performance inference configuration dictionary.
            Defaults to None.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.


    Returns:
        WorkflowPipeline: The created pipeline instance.
    """
    config = config.copy()
    if use_hpip is None:
        use_hpip = config.pop("use_hpip", False)
    else:
        config.pop("use_hpip", None)
    if hpi_config is None:
        hpi_config = config.pop("hpi_config", None)
    else:
        config.pop("hpi_config", None)

    pipeline = WorkflowPipeline(
        config=config,
        device=device,
        pp_option=pp_option,
        use_hpip=use_hpip,
        hpi_config=hpi_config,
        *args,
        **kwargs,
    )
    return pipeline