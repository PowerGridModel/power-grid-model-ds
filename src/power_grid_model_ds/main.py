from power_grid_model_ds._core.model.arrays.pgm_arrays import AsymVoltageSensorArray

dtype = AsymVoltageSensorArray.get_dtype()
print(dtype)
print(dtype["id"].metadata)
