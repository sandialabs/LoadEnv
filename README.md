# LoadEnv

> **Note:**  The following README contents are just a placeholder until this
> tool is more polished.

`LoadEnv` is a tool to allow you to consistently load reproducible
environments.

## Getting Started

1. Ensure your public ssh key is added to your gitlab-ex account:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```
   Copy the public key and add it to
   https://github.com/-/profile/keys via your browser.

2. Clone the repository:
   ```bash
   git clone git@github.com:sandialabs/code/loadenv
   ```

3. Make sure Python 3.6+ is installed.

4. Install the requirements:
   ```bash
    cd loadenv
   ./get_dependencies.sh
   ```

5. Use the script:
   ```bash
   source load-env.sh --help
   source load-env.sh --list-envs
   source load-env.sh <build-name>
   source load-env.sh Project-Name-build-Trilinos_rhel7_clang-openmp_opt_static # e.g.
   #                                                    ^__________^___ environment alias
   exit
   ```

> **Note:**  The first run of `load-env.sh` may take some time as Python
> generates byte-code for the requirements.

### Specifying the `<build-name>`

`LoadEnv` chooses the environment to load based on what it parses in the `<build-name>`.
To view available options, you can run:
```
$ source load-env.sh --list-envs
Using system 'ats1' based on matching hostname 'ats1_host'.

+==============================================================================+
|   INFO:  Please select one of the following.
|
|   - Supported Environments for 'ats1':
|     - intel-19.0.4-mpich-7.7.15-hsw-openmp
|       * Aliases:
|         - default-env-hsw
|         - intel-hsw
|         - intel-hsw-openmp
|     - intel-19.0.4-mpich-7.7.15-knl-openmp
|       * Aliases:
|         - default-env-knl
|         - intel-knl
|         - intel-knl-openmp
|
|   See `ini_files/supported-envs.ini` for details on the available environments.
|
|   To force-load an environment see the guidance in the `--help` output.
|
+==============================================================================+
```

If you wanted to load `intel-19.0.4-mpich-7.7.15-hsw-openmp`, for example, you could
include either that environment name explicitly or one of its aliases:
```bash
# The following would load the same environment:
$ source load-env.sh intel-19.0.4-mpich-7.7.15-hsw-openmp
#                    ^__________________________________^-- Full environment name
$ source load-env.sh Project-Name-build-Trilinos_ats1_intel-hsw
#                                                     ^_______^-- Alias
$ source load-env.sh Project-Name-build-Trilinos_ats1_intel-hsw-openmp_debug_static
#                                               ^    ^                ^     ^
#          Underscore is the delimiter between sys-name, env alias, & config flags
```

### Interactive mode
```bash
source load-env.sh <build-name>
```

By default, `load-env.sh` runs in interactive mode. In this mode, `load-env.sh` drops the user
to a subshell where the environment is loaded. In this way, when the user is done, they can
return to their previous environment by typing `exit`. This mode is often useful in development
environments when users are creating new environments by modifying ini files.

### CI mode
```bash
source load-env.sh --ci-mode <build-name>
```

When passing the `--ci-mode` flag to `load-env.sh`, your current shell's environment will be
overwritten by `load-env.sh`. This mode is often useful in production environments when running
`load-env.sh` from a CI driver script.


## LoadEnv API

### Installing requirements
You will need to follow the [Getting Started](https://github.com/sandialabs/loadenv#getting-started)
instructions up through step 4. before attempting to load the `LoadEnv` module.

### LoadEnv API Documentation
Please click the 'docs' badge at the top of this file or navigate [here](http://localhost:8080/LoadEnv/doc/index.html)
 with your browser for the LoadEnv API documentation.

> **Note:** When using LoadEnv in your python code, the environment will only
exist in the python process you've run `import LoadEnv` from, not the shell which that
python process was run from.
