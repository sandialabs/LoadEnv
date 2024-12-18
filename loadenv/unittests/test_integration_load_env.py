from pathlib import Path
import pytest
import sys
from unittest.mock import patch, Mock


if (Path.cwd() / "conftest.py").exists():
    root_dir = (Path.cwd()/"../..").resolve()
elif (Path.cwd() / "unittests/conftest.py").exists():
    root_dir = (Path.cwd()/"..").resolve()
else:
    root_dir = Path.cwd()

sys.path.append(str(root_dir))
from load_env import LoadEnv
import load_env



####################################################
#  DetermineSystem + EnvKeywordParser Integration  #
####################################################
@pytest.mark.parametrize(
    "inputs",
    [
        {
            "build_name": "intel-hsw",
            "hostname": "ats1_host",
            "expected_env": "ats1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
            },
        {
            "build_name": "arm",
            "hostname": "van1-tx2_host",
            "expected_env": "van1-tx2_arm-20.0-openmpi-4.0.2-openmp",
            },
        ],
    )
@patch("socket.gethostname")
def test_ekp_matches_correct_env_name(mock_gethostname, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_gethostname.return_value = inputs["hostname"]

    le = LoadEnv(argv=[inputs["build_name"]], load_env_ini_file="test_load_env.ini")
    assert le.parsed_env_name == inputs["expected_env"]



@pytest.mark.parametrize(
    "inputs_2",
    [
        {
            "build_name": "intel-knl_config_options_here_2",
            "hostname": "ats1_host",
            "expected_env_name": "ats1_intel-19.0.4-mpich-7.7.15-knl-openmp",
            "expected_sys_name": "ats1",
            },
        {
            "build_name": "arm-serial_config_options_here_2",
            "hostname": "van1-tx2_host",
            "expected_env_name": "van1-tx2_arm-20.0-openmpi-4.0.2-serial",
            "expected_sys_name": "van1-tx2",
            },
        ],
    )
@patch("socket.gethostname")
def test_loadenv_obj_can_be_reused_for_multiple_build_names(mock_gethostname, inputs_2):
    inputs_1 = {
        "build_name": "intel-hsw_config_options_here",
        "hostname": "ats1_host",
        "expected_env_name": "ats1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
        "expected_sys_name": "ats1",
        }
    mock_gethostname.return_value = inputs_1["hostname"]

    le = LoadEnv(
        argv=[
            "--supported-systems",
            "test_supported_systems.ini",
            "--supported-envs",
            "test_supported_envs.ini",
            "--environment-specs",
            "test_environment_specs.ini",
            inputs_1["build_name"],
            ]
        )
    # Sanity check / for the coverage
    assert le.build_name == inputs_1["build_name"]
    le.build_name = inputs_1["build_name"]
    assert le.build_name == inputs_1["build_name"]

    assert le.parsed_env_name == inputs_1["expected_env_name"]
    assert le.system_name == inputs_1["expected_sys_name"]
    assert le.env_stripped_build_name == "config_options_here"

    mock_gethostname.return_value = inputs_2["hostname"]
    le.build_name = inputs_2["build_name"]
    assert le.parsed_env_name == inputs_2["expected_env_name"]
    assert le.system_name == inputs_2["expected_sys_name"]
    assert le.env_stripped_build_name == "config_options_here_2"


@pytest.mark.parametrize("build_name", [
    "rhel7_cuda_config_options_here",
    "ats1_intel-19.0.4-mpich-7.7.15-hsw-openmp_config_options_here",
    "ats1_intel_config_options_here",
    "ats1_intel-hsw_config_options_here",
    "van1-tx2_arm-openmp_config_options_here",
])
def test_env_stripped_build_name_produced_correctly(build_name):
    le = LoadEnv(
        argv=[
            "--supported-systems",
            "test_supported_systems.ini",
            "--supported-envs",
            "test_supported_envs.ini",
            "--environment-specs",
            "test_environment_specs.ini",
            "--force",
            build_name,
            ]
        )

    assert le.env_stripped_build_name == "config_options_here"
    # One more time for the coverage
    assert le.env_stripped_build_name == "config_options_here"


#####################################################################
#  DetermineSystem + EnvKeywordParser + SetEnvironment Integration  #
#####################################################################
@pytest.mark.parametrize(
    "inputs",
    [
        {
            "build_name":
                "intel-hsw",
            "hostname":
                "ats1_host",
            "expected_env":
                "ats1_intel-19.0.4-mpich-7.7.15-hsw-openmp",
            "expected_cmds":
                [
                    'module load sparc-dev/intel-19.0.4_mpich-7.7.15_hsw',
                    'envvar_op set "OMP_NUM_THREADS" "2"',
                    'envvar_op unset "OMP_PLACES"',
                    'envvar_op prepend "PATH" "/path/to/atdm/ninja-1.8.2/bin"',
                    'envvar_op set "LDFLAGS" "-L/path/to/gcc/x86_64-suse-linux/8.3.0/ -lpthread ${LDFLAGS}"',
                    'envvar_op set "LDFLAGS" "-L${MPI_ROOT}/lib -lmpich -lrt ${ATP_INSTALL_DIR}/lib/libAtpSigHandler.a ${ATP_INSTALL_DIR}/lib/libbreakpad_client_nostdlib.a ${LDFLAGS}"',
                    'envvar_op find_in_path "MPICXX" "CC"',
                    'envvar_op find_in_path "MPICC" "cc"',
                    'envvar_op find_in_path "MPIF90" "ftn"',
                    'envvar_op set "CXX" "${MPICXX}"',
                    'envvar_op set "CC" "${MPICC}"',
                    'envvar_op set "F77" "${MPIF90}"',
                    'envvar_op set "FC" "${MPIF90}"',
                    'envvar_op set "F90" "${MPIF90}"',
                    ],
            },
        {
            "build_name":
                "arm",
            "hostname":
                "van1-tx2_host",
            "expected_env":
                "van1-tx2_arm-20.0-openmpi-4.0.2-openmp",
            "expected_cmds":
                [
                    'module purge',
                    'module load devpack-arm/1.2.3',
                    'module unload yaml-cpp',
                    'module load ninja',
                    'module load cmake/3.17.1',
                    'envvar_op set "MPI_ROOT" "${MPI_DIR}"',
                    'envvar_op set "BLAS_ROOT" "${ARMPL_DIR}"',
                    'envvar_op set "HDF5_ROOT" "${HDF5_DIR}"',
                    'envvar_op set "NETCDF_ROOT" "${NETCDF_DIR}"',
                    'envvar_op set "PNETCDF_ROOT" "${PNETCDF_DIR}"',
                    'envvar_op set "ZLIB_ROOT" "${ZLIB_DIR}"',
                    'envvar_op set "CGNS_ROOT" "${CGNS_DIR}"',
                    'envvar_op set "BOOST_ROOT" "${BOOST_DIR}"',
                    'envvar_op set "METIS_ROOT" "${METIS_DIR}"',
                    'envvar_op set "PARMETIS_ROOT" "${PARMETIS_DIR}"',
                    'envvar_op set "SUPERLUDIST_ROOT" "${SUPLERLU_DIST_DIR}"',
                    'envvar_op set "BINUTILS_ROOT" "${BINUTILS_DIR}"',
                    'envvar_op unset "HWLOC_LIBS"',
                    'envvar_op set "CC" "mpicc"',
                    'envvar_op set "CXX" "mpicxx"',
                    'envvar_op set "FC" "mpif77"',
                    'envvar_op set "F90" "mpif90"',
                    'envvar_op set "FC" "mpif90"',
                    'envvar_op find_in_path "MPICC" "mpicc"',
                    'envvar_op find_in_path "MPICXX" "mpicxx"',
                    'envvar_op find_in_path "MPIF90" "mpif90"',
                    'envvar_op set "OMP_NUM_THREADS" "2"',
                    ],
            },
        ],
    )
@patch("socket.gethostname")
def test_correct_commands_are_saved(mock_gethostname, inputs):
    ###########################################################################
    # **This will need to change later once we have a more sophisticated**
    # **system determination in place.**
    ###########################################################################
    mock_gethostname.return_value = inputs["hostname"]
    le = LoadEnv(
        argv=[
            "--supported-systems",
            "test_supported_systems.ini",
            "--supported-envs",
            "test_supported_envs.ini",
            "--environment-specs",
            "test_environment_specs.ini",
            inputs["build_name"],
            ]
        )
    assert le.parsed_env_name == inputs["expected_env"]

    le.write_load_matching_env()
    with open(le.tmp_load_matching_env_file, "r") as f:
        load_matching_env_contents = f.read()

    for expected_cmd in inputs["expected_cmds"]:
        assert expected_cmd in load_matching_env_contents



@pytest.mark.parametrize("output", [None, "test_dir/load_matching_env.sh"])
@patch("socket.gethostname")
def test_load_matching_env_is_set_correctly_and_directories_are_created(mock_gethostname, output):
    if output is not None:
        assert Path(output).exists() is False

    mock_gethostname.return_value = "van1-tx2_host"
    argv = ["arm"] if output is None else ["arm", "--output", output]
    le = LoadEnv(argv=argv, load_env_ini_file="test_load_env.ini")
    load_matching_env = le.write_load_matching_env()

    expected_file = (le.tmp_load_matching_env_file if output is None else Path(output)).resolve()
    assert expected_file.parent.exists()
    assert load_matching_env == expected_file


@patch("socket.gethostname")
def test_existing_load_matching_env_file_overwritten(mock_gethostname):
    output_file = "test_load_matching_env.sh"
    initial_contents = "test file contents"
    with open(output_file, "w") as F:
        F.write(initial_contents)

    mock_gethostname.return_value = "van1-tx2_host"
    le = LoadEnv(argv=["arm", "--output", output_file], load_env_ini_file="test_load_env.ini")

    load_matching_env = le.write_load_matching_env()
    with open(le.tmp_load_matching_env_file, "r") as F:
        load_matching_env_contents = F.read()

    assert initial_contents != load_matching_env_contents


#  main()  #
############
@patch("socket.gethostname")
@patch("load_env.SetEnvironment")
def test_main_with_successful_apply(mock_set_environment, mock_gethostname):
    mock_gethostname.return_value = "van1-tx2_host"
    # 'unsafe=True' allows methods to be called on the mock object that start
    # with 'assert'. For SetEnvironment, this includes
    # 'assert_file_all_sections_handled'.
    mock_se = Mock(unsafe=True)
    mock_se.apply.return_value = 0
    mock_set_environment.return_value = mock_se

    load_env.main([
        "--supported-systems", "test_supported_systems.ini",
        "--supported-envs", "test_supported_envs.ini",
        "--environment-specs", "test_environment_specs.ini",
        "arm",
        "--output", "test_out.sh"
    ])


@patch("socket.gethostname")
@patch("load_env.SetEnvironment")
def test_main_with_unsuccessful_apply(mock_set_environment, mock_gethostname):
    mock_gethostname.return_value = "van1-tx2_host"
    mock_se = Mock(unsafe=True)
    mock_se.apply.return_value = 1
    mock_set_environment.return_value = mock_se

    expected_exc_msg = "Something unexpected went wrong in applying the environment."
    with pytest.raises(RuntimeError, match=expected_exc_msg):
        load_env.main([
            "--supported-systems", "test_supported_systems.ini",
            "--supported-envs", "test_supported_envs.ini",
            "--environment-specs", "test_environment_specs.ini",
            "arm",
            "--output", "test_out.sh"
        ])


# Operation Validation
# ====================
@pytest.mark.parametrize("data", [
    {
        "operations": ["use"],
        "invalid": [],
        "should_raise": False
    },
    {
        "operations": ["use", "invalid-operation"],
        "invalid": ["invalid-operation"],
        "should_raise": True
    },
    {
        "operations": ["invalid-operation", "invalid-operation-2"],
        "invalid": ["invalid-operation", "invalid-operation-2"],
        "should_raise": True
    },
    {
        "operations": ["use", "invalidOperationNoDashes"],
        "invalid": ["invalidOperationNoDashes"],
        "should_raise": True
    },
])
def test_invalid_operations_raises(data):
    valid_section_name = "ats1_intel-19.0.4-mpich-7.7.15-hsw-openmp"
    bad_environment_specs = ("[ATS1]\n"
                             "module-load cmake: 3.18.0\n\n"
                             f"[{valid_section_name}]\n")
    for operation in data["operations"]:
        bad_environment_specs += ("use ATS1\n"
                                  if operation == "use"
                                  else f"{operation} params for op: here\n")

    test_ini_filename = "test_generated_environment_specs_invalid_operations.ini"
    with open(test_ini_filename, "w") as F:
        F.write(bad_environment_specs)

    le = LoadEnv([
        "--supported-envs", "test_supported_envs.ini",
        "--environment-specs", test_ini_filename,
        "--force",
        "ats1_intel"
    ])


    if data["should_raise"]:
        with pytest.raises(ValueError):
            le.load_set_environment()
    else:
        le.load_set_environment()
