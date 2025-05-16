import tensorflow as tf
print("Built with CUDA:", tf.test.is_built_with_cuda())
print("CUDA Version :", tf.sysconfig.get_build_info().get("cuda_version"))
print("cuDNN Version:", tf.sysconfig.get_build_info().get("cudnn_version"))
print("Physical GPUs:", tf.config.list_physical_devices("GPU"))