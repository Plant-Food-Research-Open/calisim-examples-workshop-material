import pandas as pd

from calisim.base import CalibrationWorkflowBase
from calisim.data_model import (
	DistributionModel,
	ParameterDataType,
	ParameterSpecification,
)
from calisim.experimental.state_estimation import (
	StateEstimationMethod,
	StateEstimationMethodModel,
)
from calisim.utils import get_examples_outdir
from pcse.models import Wofost72_WLP_FD
from dataproviders import parameters, agromanagement, weather

wofost = Wofost72_WLP_FD(parameters, weather, agromanagement)
wofost.run_till_terminate()
df = pd.DataFrame(wofost.get_output())[50:5025:150].set_index("day")
import copy
true_params = {}
true_params["TDWI"] = 160
true_params["WAV"] = 5
true_params["SPAN"] = 33
true_params["SMFCF"] = .33
n_iterations = 150

p = copy.deepcopy(parameters)
for par, distr in true_params.items():
    p.set_override(par, distr)
ground_truth = Wofost72_WLP_FD(p, weather, agromanagement)
ground_truth.run_till_terminate()

observed_df = pd.DataFrame(ground_truth.get_output()).set_index("day")

parameter_spec = ParameterSpecification(
    parameters=[
        DistributionModel(
            name="TDWI",
            distribution_name="normal",
            distribution_args=[150, 50],
            data_type=ParameterDataType.CONTINUOUS,
        ),
        DistributionModel(
            name="WAV",
            distribution_name="normal",
            distribution_args=[4.5, 1.55],
            data_type=ParameterDataType.CONTINUOUS,
        ),
        DistributionModel(
            name="SPAN",
            distribution_name="normal",
            distribution_args=[31, 3],
            data_type=ParameterDataType.CONTINUOUS,
        ),
        DistributionModel(
            name="SMFCF",
            distribution_name="normal",
            distribution_args=[0.31, 0.03],
            data_type=ParameterDataType.CONTINUOUS,
        )
    ]
)

def state_estimation_func(
    sample_parameters: dict, simulation_id: str, observed_data: pd.DataFrame | None,
    t: pd.Series, calibration_workflow: CalibrationWorkflowBase
) -> float | list[float]:
    current_step = calibration_workflow.t
    ensemble = calibration_workflow.get_ensemble()
    timesteps = set(t)

    if current_step == -1:
        p = copy.deepcopy(parameters)
        for par, distr in sample_parameters.items():
            p.set_override(par, distr)
        ensemble[simulation_id]["model"] = Wofost72_WLP_FD(p, weather, agromanagement)

    model = ensemble[simulation_id]["model"]
    model.run(1)
    output = model.get_output()[-1]
    LAI = output["LAI"]
    ensemble[simulation_id]["result"]["LAI"].append(LAI)

    current_date = output["day"]
    if current_date in timesteps:
        calibration_workflow.perform_update = True

outdir = get_examples_outdir()
specification = StateEstimationMethodModel(
    experiment_name="ekf_state_estimation",
    parameter_spec=parameter_spec,
    observed_data=observed_df,
    outdir=outdir,
    n_samples=25,
    n_iterations=n_iterations,
    output_labels=["LAI"],
    stds = dict(LAI=0.05),
    verbose=True,
    batched=False,
    calibration_func_kwargs=dict(t=observed_df.index),
    method_kwargs=dict(truncation=1.0),
)

calibrator = StateEstimationMethod(
    calibration_func=state_estimation_func, specification=specification, engine="ekf"
)

calibrator.specify().execute().analyze()

result_artifacts = "\n".join(calibrator.get_artifacts())
print(f"View results: \n{result_artifacts}")
