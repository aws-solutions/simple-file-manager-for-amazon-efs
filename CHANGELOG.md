# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2021-07-08
- General bug fixes 
- Code refactoring to support pylint
- cfn-lint / bandit code cleanup
- Misc documentation

## [1.3.0] - 2021-06-01
## New:
- Add delete functionality for SFM created resources #115 

## Security:
- IAM permissions scoped down  #114

## Documentation:
Diagrams from previous update
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
Diagrams from previous update
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
