# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.6] - 2024-04-09
### Fixed
- Updated axios sub-dependency to use v0.28.0 to resolve security vulnerabilities:
  - [CVE-2023-45857]
  - [CVE-2024-28849]
  - [CVE-2023-26159]

- Re-generated package-lock to resolve security vulnerabilities:
  - [CVE-2024-29180]
  - [CVE-2023-42282]
  - [CVE-2024-29041]

## [1.5.5] - 2023-10-20
### Fixed:
- Updated crypto.js dependency to fix security vulnerabilities [CVE-2023-46233]
- Updated react-dev-tools dependency to fix security vulnerabilities [CVE-2023-5654]
- Update urllib3 dependency to v1.26.18

## [1.5.4] - 2023-10-20
### Fixed:
- Fixing Security Vulnerabilities

## [1.5.3] - 2023-09-20
### Bug Fixes:
- Merge Website Bucket policy statements to prevent deployment failures on policy creation slowdowns
- Remove uneeded exit in Unit test script
- Added downline dependencies to NOTICE.txt

### Security:
- Upgrade Node version to 18
- Upgrade Python runtime to 3.11
- Update NPM packages to fix vulnerabilities

## [1.5.2] - 2023-05-19
### Bug Fixes:
- elasticfilesystem:TagResource permission added to Manager Lambda
- Urllib3 downgraded to < v2

## [1.5.1] - 2023-04-13
### Security:
- Enable versioning/encryption on logging bucket 

### Bug Fixes:
- Enable Amazon S3 ACLs on logging bucket
- Include package-lock.json to prevent incompatibilities with future package versions

## [1.5.0] - 2022-10-17
### New:
- Paginated response for list filesystems that allows greater than 10 EFS filesystems to be displayed
- AppRegistry Integration
- File manager lambda creation now checks for valid security group rules

### Changes:
- Code refactoring to reduce cognitive complexity
- Buildspec upgrades
- Unit tests to 80% overall coverage

### Documentation:
- Misc documentation

## [1.4.1] - 2022-08-24
### Changes:
- Python version bump to handle 3.6 EOL

## [1.4.0] - 2021-07-08
### Changes:
- Code refactoring to support pylint
- cfn-lint / bandit code cleanup

### Bug Fixes:
- General bug fixes 

### Documentation:
- Misc documentation

## [1.3.0] - 2021-06-01
### New:
- Add delete functionality for SFM created resources #115 

### Security:
- IAM permissions scoped down  #114

### Documentation:
- Diagrams from previous update
- Detailed architecture diagram #1
- Simplified architecture diagram #1
- Security sequence diagram #1


## [1.2.0] - 2021-05-26
### New:
- Fix rollback issue when file manager lambda is not created successfully #67 
- Allow upload modal to be closed if upload fails #79 
- Check if file exists before attempting upload #77 

### Changes:
- Generate pop up for deleting files instead of an alert #66 
- Added Nightly Tests

### Security:
- IAM permissions scoped down for CloudFormation templates. #61 
- CFN Nag changes for Lambdas deployed into a VPC #63 
- Changes so uses a minimum of CloudFront TLS 1.2 #62 
- EFS-File-Manager.yaml IAM update to use iam:passedtoservice condition key #81 

### Bug Fixes:
- FS lambda fails to launch due to SG constraint #75 

### Documentation:
- Diagrams from previous update
- Detailed architecture diagram #1
- Simplified architecture diagram #1
- Security sequence diagram #1


## [1.1.0] - 2021-04-26
### New:
- File manager creation now accepts a custom UID, GID, and Path #22
- File manager lambda automatically attaches to all available mount targets #9
- Added the filesystem name to the filesystems table #41

### Changes:
- Render a message saying no filesystems found when there are no EFS filesystems in the account instead of an empty table #46
- Added a creating state to indicate that the file manager lambda is still being created #42
- User agent string is being sent to identify the application #52
- /download and /upload moved underneath the /objects path #45

### Security:
N/A

### Bug Fixes:
- Removed the sign up option on login page which was producing an error #44

### Documentation:
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
