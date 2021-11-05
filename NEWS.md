ionit 0.4.0 (2021-11-05)
========================

* Add `--encoding` option and default it to `utf-8`
* Drop support for Python < 3.6
* Fix issues found by pylint 2.11.1
  (fixes [Debian bug #998574](https://bugs.debian.org/998574)):
  * tests: Use `with` for `subprocess.Popen` calls
  * Use `from ruamel import yaml`
  * Replace `.format()` with f-strings

ionit 0.3.7 (2021-05-21)
========================

* tests: Mark `ionit_plugin` as first party module

ionit 0.3.7 (2021-05-20)
========================

* Check import definition order with isort
* Fix code format for older black versions
* Add test case for black code formatter
* Fix YAMLLoadWarning with PyYAML 5.1+
* Add support for ruamel.yaml
* `setup.py`: Add PyYAML as dependency

ionit 0.3.6 (2020-09-28)
========================

* Address issues found by pylint 2.6.0
  (fixes [Debian bug #971138](https://bugs.debian.org/971138))
* Blacken Python code

ionit 0.3.5 (2020-01-17)
========================

* Run `ionit.service` before `ifupdown-pre.service`

ionit 0.3.4 (2019-12-03)
========================

* Fix issues found by pylint 2.4.4
  (fixes [Debian bug #946034](https://bugs.debian.org/946034))

ionit 0.3.3 (2019-07-08)
========================

* Drop `After=local-fs.target` from `ionit.service` to break dependency loop
  (fixes [Debian bug #931060](https://bugs.debian.org/931060))

ionit 0.3.2 (2019-06-20)
========================

* Run `ionit.service` before `systemd-udev-trigger.service`
  (fixes [Debian bug #919690](https://bugs.debian.org/919690))

ionit 0.3.1 (2019-04-11)
========================

* Run `ionit.service` before `systemd-modules-load.service`

ionit 0.3.0 (2019-02-20)
========================

* Support specifying a configuration file (instead of a directory)
* Support specifying `--config` multiple times

ionit 0.2.1 (2019-01-07)
========================

* Remove unnecessary pass statement to make pylint 2.2.2 happy
  (fixes [Debian bug #918550](https://bugs.debian.org/918550))

ionit 0.2 (2018-11-12)
======================

* Prevent false warning if `collect_context` returns empty dictionary
* Run ionit service before ferm service
* Fix loading different Python modules with the same name
  (for tests with Python < 3.5)
* Ignore deprecation warning for backward compatibility code

ionit 0.1 (2018-08-16)
======================

* Initial release
