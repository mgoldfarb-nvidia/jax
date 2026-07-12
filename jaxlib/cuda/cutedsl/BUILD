load("@bazel_skylib//rules:common_settings.bzl", "bool_flag")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_cc//cc:cc_test.bzl", "cc_test")

# Keep production calls direct while intercepting the runtime C ABI in unit
# tests that exercise invalid module images and injected failures.
_RUNTIME_TEST_LINKOPTS = [
    "-Wl,--wrap=CuteDSLRT_Function_Run",
    "-Wl,--wrap=CuteDSLRT_GetErrorName",
    "-Wl,--wrap=CuteDSLRT_GetErrorString",
    "-Wl,--wrap=CuteDSLRT_Module_Create_From_Bytes",
    "-Wl,--wrap=CuteDSLRT_Module_Destroy",
    "-Wl,--wrap=CuteDSLRT_Module_Get_Function",
]

package(
    default_applicable_licenses = [],
    default_visibility = ["//jax:internal"],
)

licenses(["notice"])

cc_library(
    name = "runtime_unavailable",
    visibility = ["//jax_plugins/cuda:__pkg__"],
)

label_flag(
    name = "cutedsl_runtime",
    build_setting_default = ":runtime_unavailable",
    visibility = ["//visibility:public"],
)

label_flag(
    name = "cutedsl_runtime_dso",
    build_setting_default = ":runtime_unavailable",
    visibility = ["//visibility:public"],
)

bool_flag(
    name = "cutedsl_runtime_is_shared",
    build_setting_default = False,
    visibility = ["//visibility:public"],
)

config_setting(
    name = "cutedsl_runtime_unavailable_selected",
    flag_values = {
        ":cutedsl_runtime": "//jaxlib/cuda/cutedsl:runtime_unavailable",
    },
)

config_setting(
    name = "cutedsl_runtime_shared_selected",
    flag_values = {
        ":cutedsl_runtime_is_shared": "true",
    },
    visibility = ["//jax_plugins/cuda:__pkg__"],
)

_RUNTIME_TARGET_COMPATIBILITY = select({
    ":cutedsl_runtime_unavailable_selected": ["@platforms//:incompatible"],
    "//conditions:default": [],
})

cc_library(
    name = "module",
    srcs = ["module.cc"],
    hdrs = ["module.h"],
    linkopts = select({
        "@platforms//os:linux": ["-Wl,-rpath,$$ORIGIN"],
        "//conditions:default": [],
    }),
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":cutedsl_runtime",
        "@com_google_absl//absl/base:core_headers",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:str_format",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_absl//absl/synchronization",
        "@llvm-project//llvm:Support",
    ],
)

cc_library(
    name = "ffi_abi",
    hdrs = ["ffi_abi.h"],
)

cc_library(
    name = "collective_config",
    srcs = ["collective_config.cc"],
    hdrs = ["collective_config.h"],
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":module",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:str_format",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_absl//absl/types:span",
        "@xla//xla:xla_data_proto_cc",
        "@xla//xla/ffi",
        "@xla//xla/tsl/platform:status_macros",
    ],
)

cc_library(
    name = "collective_ffi",
    srcs = [
        "collective_ffi.cc",
        "@xla//xla/ffi/api:all_headers",
    ],
    hdrs = ["collective_ffi.h"],
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":collective_config",
        ":ffi_abi",
        ":module",
        "@com_google_absl//absl/algorithm:container",
        "@com_google_absl//absl/container:btree",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/log",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings",
        "@com_google_absl//absl/strings:str_format",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_absl//absl/types:span",
        "@xla//xla:xla_data_proto_cc",
        "@xla//xla/backends/gpu:ffi",
        "@xla//xla/backends/gpu/collectives:gpu_clique_key",
        "@xla//xla/backends/gpu/collectives:gpu_communicator",
        "@xla//xla/backends/gpu/runtime:collective_clique_requests",
        "@xla//xla/backends/gpu/runtime:collective_cliques",
        "@xla//xla/backends/gpu/runtime:collective_execution",
        "@xla//xla/backends/gpu/runtime:collective_kernel_api",
        "@xla//xla/backends/gpu/runtime:collective_memory",
        "@xla//xla/backends/gpu/runtime:collective_memory_requests",
        "@xla//xla/backends/gpu/runtime:collective_params",
        "@xla//xla/core/collectives:rank_id",
        "@xla//xla/core/collectives:symmetric_memory",
        "@xla//xla/ffi",
        "@xla//xla/ffi/api:c_api",
        "@xla//xla/service:collective_ops_utils",
        "@xla//xla/service:computation_placer",
        "@xla//xla/stream_executor:device_address",
        "@xla//xla/stream_executor:event",
        "@xla//xla/stream_executor:memory_allocation",
        "@xla//xla/stream_executor:memory_allocator",
        "@xla//xla/stream_executor:memory_space",
        "@xla//xla/stream_executor:stream",
        "@xla//xla/stream_executor:stream_executor_h",
        "@xla//xla/stream_executor/gpu:multi_gpu_barrier_kernel",
        "@xla//xla/tsl/platform:env",
        "@xla//xla/tsl/platform:status_macros",
        "@xla//xla/tsl/util:tied_ref",
    ],
    alwayslink = True,
)

cc_library(
    name = "ffi",
    srcs = [
        "ffi.cc",
        "@xla//xla/ffi/api:all_headers",
    ],
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":ffi_abi",
        ":module",
        "@com_google_absl//absl/base:core_headers",
        "@com_google_absl//absl/container:inlined_vector",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:str_format",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_absl//absl/synchronization",
        "@xla//xla/backends/gpu:ffi",
        "@xla//xla/ffi",
        "@xla//xla/ffi/api:c_api",
        "@xla//xla/tsl/platform:status_macros",
    ],
    alwayslink = True,
)

cc_library(
    name = "handlers",
    visibility = ["//jax_plugins/cuda:__pkg__"],
    deps = select({
        ":cutedsl_runtime_unavailable_selected": [],
        "//conditions:default": [
            ":collective_ffi",
            ":ffi",
        ],
    }),
)

cc_test(
    name = "module_test",
    srcs = ["module_test.cc"],
    linkopts = _RUNTIME_TEST_LINKOPTS,
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":cutedsl_runtime",
        ":module",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_googletest//:gtest_main",
        "@llvm-project//llvm:Support",
    ],
)

cc_test(
    name = "collective_config_test",
    srcs = ["collective_config_test.cc"],
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":collective_config",
        ":module",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_googletest//:gtest_main",
        "@llvm-project//llvm:Support",
        "@xla//xla/ffi",
        "@xla//xla/ffi:attribute_map",
        "@xla//xla/ffi:call_frame",
        "@xla//xla/ffi:ffi_api",
        "@xla//xla/ffi:invoke",
        "@xla//xla/tsl/platform:status_matchers",
    ],
)

cc_test(
    name = "collective_ffi_test",
    srcs = ["collective_ffi_test.cc"],
    linkopts = _RUNTIME_TEST_LINKOPTS,
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":collective_config",
        ":collective_ffi",
        ":cutedsl_runtime",
        ":module",
        "@com_google_absl//absl/container:flat_hash_map",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_absl//absl/types:span",
        "@com_google_googletest//:gtest_main",
        "@llvm-project//llvm:Support",
        "@xla//xla:types",
        "@xla//xla/backends/gpu/collectives:gpu_clique_key",
        "@xla//xla/backends/gpu/collectives:gpu_collectives_stub",
        "@xla//xla/backends/gpu/runtime:collective_clique_requests",
        "@xla//xla/backends/gpu/runtime:collective_cliques",
        "@xla//xla/backends/gpu/runtime:collective_memory",
        "@xla//xla/backends/gpu/runtime:collective_memory_requests",
        "@xla//xla/backends/gpu/runtime:collective_params",
        "@xla//xla/core/collectives:rank_id",
        "@xla//xla/core/collectives:symmetric_memory",
        "@xla//xla/ffi",
        "@xla//xla/ffi:attribute_map",
        "@xla//xla/ffi:call_frame",
        "@xla//xla/ffi:execution_state",
        "@xla//xla/ffi:ffi_api",
        "@xla//xla/ffi:ffi_registry",
        "@xla//xla/ffi:invoke",
        "@xla//xla/ffi/api:c_api",
        "@xla//xla/service:computation_placer",
        "@xla//xla/service:service_executable_run_options",
        "@xla//xla/service/gpu:buffer_allocations",
        "@xla//xla/service/gpu:gpu_executable_run_options",
        "@xla//xla/stream_executor:device_address",
        "@xla//xla/stream_executor:event",
        "@xla//xla/stream_executor:mock_platform",
        "@xla//xla/stream_executor:mock_stream",
        "@xla//xla/stream_executor:mock_stream_executor",
        "@xla//xla/tsl/platform:status_matchers",
    ],
)

cc_test(
    name = "ffi_unit_test",
    srcs = ["ffi_unit_test.cc"],
    linkopts = _RUNTIME_TEST_LINKOPTS,
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":cutedsl_runtime",
        ":ffi",
        "@com_google_absl//absl/status",
        "@com_google_absl//absl/status:statusor",
        "@com_google_absl//absl/strings:string_view",
        "@com_google_googletest//:gtest_main",
        "@llvm-project//llvm:Support",
        "@xla//xla:types",
        "@xla//xla/ffi",
        "@xla//xla/ffi:call_frame",
        "@xla//xla/ffi:execution_state",
        "@xla//xla/ffi:ffi_api",
        "@xla//xla/ffi:ffi_registry",
        "@xla//xla/ffi:invoke",
        "@xla//xla/ffi/api:c_api",
        "@xla//xla/stream_executor:device_address",
        "@xla//xla/stream_executor:mock_stream",
    ],
)

cc_test(
    name = "ffi_test_b200",
    srcs = ["ffi_test.cc"],
    data = ["vector_add.hlo"],
    tags = [
        "cuda-only",
        "gpu",
        "manual",
        "requires-gpu-sm100-only",
    ],
    target_compatible_with = _RUNTIME_TARGET_COMPATIBILITY,
    deps = [
        ":ffi",
        "@com_google_googletest//:gtest_main",
        "@xla//xla:literal",
        "@xla//xla:shape_util",
        "@xla//xla:types",
        "@xla//xla/hlo/builder:xla_computation",
        "@xla//xla/hlo/parser:hlo_parser",
        "@xla//xla/pjrt:pjrt_client",
        "@xla//xla/pjrt:pjrt_executable",
        "@xla//xla/pjrt/plugin/xla_gpu:xla_gpu_pjrt_client",
        "@xla//xla/service:gpu_plugin",
        "@xla//xla/stream_executor/cuda:cuda_platform",
        "@xla//xla/tsl/platform:env",
        "@xla//xla/tsl/platform:resource_loader",
        "@xla//xla/tsl/platform:statusor",
    ],
)

test_suite(
    name = "ffi_test",
    tags = ["manual"],
    tests = [":ffi_test_b200"],
)
