# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.17] - 2025-07-29

### Security

- Bump `form-data` to `4.0.4` to resolve CVE [CVE-2025-7783 ](https://avd.aquasec.com/nvd/2025/cve-2025-7783/)

## [1.5.16] - 2025-06-09

### Security

- Bump `http-proxy-middleware` to `2.0.9` to resolve CVE [CVE-2025-32996](https://avd.aquasec.com/nvd/2025/cve-2025-32996/)
- Added `webpack-dev-server` override to mitigate [CVE-2025-30359](https://avd.aquasec.com/nvd/2025/cve-2025-30359/) & [CVE-2025-30360](https://avd.aquasec.com/nvd/2025/cve-2025-30360/)

### Removed

- `aws-sdk` due to no direct usage and upcoming v2 end of support.

## [1.5.15] - 2025-04-09

### Security

- Bump child dependencies

## [1.5.14] - 2025-03-14

### Security

- Upgrade axios to `1.8.2` to resolve CVE [CVE-2025-27152](https://avd.aquasec.com/nvd/2025/cve-2025-27152/)

## [1.5.13] - 2025-02-06

### Security

- Bump nanoid to `3.3.8` to resolve CVE [CVE-2024-55565](https://github.com/advisories/GHSA-mwcw-c2x4-8c55)
- Bump path-to-regexp to`0.1.12` to resolve CVE [CVE-2024-52798](https://github.com/advisories/GHSA-rhx6-c78j-4q9w)
- Override vue dependencies to `3.4.34` to resolve CVE [CVE-2024-9506](https://github.com/advisories/GHSA-5j4c-8p2g-v4jx)

## [1.5.12] - 2024-11-19

### Security

- Bump cross-spawn to `7.0.6` to resolve [CVE-2024-9506](https://github.com/advisories/GHSA-5j4c-8p2g-v4jx)

### Fixed

- If a filesystem's stack changes from CREATE_COMPLETE to UPDATE_COMPLETE it no longer lists as managed [#229](https://github.com/aws-solutions/simple-file-manager-for-amazon-efs/issues/229)

## [1.5.11] - 2024-10-29

### Security

- Bump http-proxy-middleware to `2.0.7` to resolve [CVE-2024-21536](https://github.com/advisories/GHSA-c7qv-q95q-8v27)
- Bump cookie to `0.7.0` to resolve CVE [CVE-2024-47764](https://github.com/advisories/GHSA-pxg6-pf52-xh8x)  

## [1.5.10] - 2024-09-20

### Security

- Bump webpack to `5.94.0` to resolve [CVE-2024-43788](https://github.com/advisories/GHSA-4vvj-4cpr-p986)
- Bump serve-static to `1.16.2` to resolve CVE with send [CVE-2024-43799](https://github.com/advisories/GHSA-m6fv-jmcg-4jfg)
- Bump path-to-regexp to `0.1.10` to resolve [CVE-2024-45296](https://github.com/advisories/GHSA-9wv6-86v2-598j)
- Bump micromatch to `4.0.8` to resolve [CVE-2024-4067](https://github.com/advisories/GHSA-952p-6rrq-rcjv)
- Remove usage of `bootstrap-vue` (EOL) and migrate `bootstrap v4` (EOL) to `bootstrap v5` to resolve [CVE-2024-6531](https://nvd.nist.gov/vuln/detail/CVE-2024-6531)
- Adds Security.md file to provide guidance around reporting security vulnerabilities.

## [1.5.9] - 2024-08-02

### Security

- Bump `fast-xml-parser` to `4.4.1` to resolve [CVE-2024-41818](https://nvd.nist.gov/vuln/detail/CVE-2024-41818)
- Update to Vue 3 compat build and replace `vue-template-compiler` with `@vue/compiler-sfc` to resolve [CVE-2024-6783](https://nvd.nist.gov/vuln/detail/CVE-2024-6783)

### Removed

- Unused `vue-stepper-component` and `vue2-dropzone` dependencies

## [1.5.8] - 2024-06-23

### Security

- Bump `braces` to `3.0.3` to resolve [CVE-2024-4068](https://nvd.nist.gov/vuln/detail/CVE-2024-4068)
- Bump `ws` to resolve [CVE-2024-37890](https://nvd.nist.gov/vuln/detail/CVE-2024-37890)

## [1.5.7] - 2024-05-30

### Fixed

- Updated API Handler Python runtime to 3.11 due to Python 3.8 Lambda runtime deprecation

### Changed

- Updated spoke template descriptions to include suffix

## [1.5.6] - 2024-04-09

### Fixed

- Updated axios sub-dependency to use v0.28.0 to resolve security vulnerabilities:
  - [CVE-2023-45857](https://nvd.nist.gov/vuln/detail/CVE-2023-45857)
  - [CVE-2024-28849](https://nvd.nist.gov/vuln/detail/CVE-2024-28849)
  - [CVE-2023-26159](https://nvd.nist.gov/vuln/detail/CVE-2023-26159)

- Re-generated package-lock to resolve security vulnerabilities:
  - [CVE-2024-29180](https://nvd.nist.gov/vuln/detail/CVE-2024-29180)
  - [CVE-2023-42282](https://nvd.nist.gov/vuln/detail/CVE-2023-42282)
  - [CVE-2024-29041](https://nvd.nist.gov/vuln/detail/CVE-2024-29041)

## [1.5.5] - 2023-10-20

### Fixed

- Updated crypto.js dependency to fix security vulnerabilities [CVE-2023-46233](https://nvd.nist.gov/vuln/detail/CVE-2023-46233)
- Updated react-dev-tools dependency to fix security vulnerabilities [CVE-2023-5654](https://nvd.nist.gov/vuln/detail/CVE-2023-5654)
- Update urllib3 dependency to v1.26.18

## [1.5.4] - 2023-10-20

### Fixed

- Fixing Security Vulnerabilities

## [1.5.3] - 2023-09-20

### Fixed

- Merge Website Bucket policy statements to prevent deployment failures on policy creation slowdowns
- Remove uneeded exit in Unit test script
- Added downline dependencies to NOTICE.txt

### Security

- Upgrade Node version to 18
- Upgrade Python runtime to 3.11
- Update NPM packages to fix vulnerabilities

## [1.5.2] - 2023-05-19

### Fixed

- elasticfilesystem:TagResource permission added to Manager Lambda
- Urllib3 downgraded to < v2

## [1.5.1] - 2023-04-13

### Security

- Enable versioning/encryption on logging bucket

### Fixed

- Enable Amazon S3 ACLs on logging bucket
- Include package-lock.json to prevent incompatibilities with future package versions

## [1.5.0] - 2022-10-17

### Added

- Paginated response for list filesystems that allows greater than 10 EFS filesystems to be displayed
- AppRegistry Integration
- File manager lambda creation now checks for valid security group rules

### Changed

- Code refactoring to reduce cognitive complexity
- Buildspec upgrades
- Unit tests to 80% overall coverage

### Added

- Misc documentation

## [1.4.1] - 2022-08-24

### Changed

- Python version bump to handle 3.6 EOL

## [1.4.0] - 2021-07-08

### Changed

- Code refactoring to support pylint
- cfn-lint / bandit code cleanup

### Fixed

- General bug fixes

### Added

- Misc documentation

## [1.3.0] - 2021-06-01

### Added

- Add delete functionality for SFM created resources #115
- Diagrams from previous update
- Detailed architecture diagram #1
- Simplified architecture diagram #1
- Security sequence diagram #1

### Security

- IAM permissions scoped down  #114

## [1.2.0] - 2021-05-26

### Added

- Fix rollback issue when file manager lambda is not created successfully #67
- Allow upload modal to be closed if upload fails #79
- Check if file exists before attempting upload #77

### Changed

- Generate pop up for deleting files instead of an alert #66
- Added Nightly Tests

### Security

- IAM permissions scoped down for CloudFormation templates. #61
- CFN Nag changes for Lambdas deployed into a VPC #63
- Changes so uses a minimum of CloudFront TLS 1.2 #62
- EFS-File-Manager.yaml IAM update to use iam:passedtoservice condition key #81

### Fixed

- FS lambda fails to launch due to SG constraint #75

### Added

- Diagrams from previous update
- Detailed architecture diagram #1
- Simplified architecture diagram #1
- Security sequence diagram #1

## [1.1.0] - 2021-04-26

### Added

- File manager creation now accepts a custom UID, GID, and Path #22
- File manager lambda automatically attaches to all available mount targets #9
- Added the filesystem name to the filesystems table #41

### Changed

- Render a message saying no filesystems found when there are no EFS filesystems in the account instead of an empty table #46
- Added a creating state to indicate that the file manager lambda is still being created #42
- User agent string is being sent to identify the application #52
- /download and /upload moved underneath the /objects path #45

### Security

N/A

### Fixed

- Removed the sign up option on login page which was producing an error #44

### Added

- Detailed architecture diagram #1
- Simplified architecture diagram #1
- Security sequence diagram #1

## [1.0.0] - 2021-04-09

### Added

- example-function-js sample microservice
- added unit tests for example-function-js

### Changed

- example.template to yaml file example with JS.
- updated build-s3-dist.sh script to include soltion-name parameter
- updated build-open-source.sh script to include soltion-name parameter
- updated run-unit-tests.sh script to execute example-function-js unit tests

### Removed

- deployment/buildspec files.
- helper function

## [0.0.1] - 2019-04-15

### Added

- CHANGELOG templated file
- README templated file
- NOTICE file
- LICENSE file
