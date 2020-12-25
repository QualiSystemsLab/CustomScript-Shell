[![Coverage Status](https://coveralls.io/repos/github/QualiSystems/CustomScript-Shell/badge.svg?branch=develop)](https://coveralls.io/github/QualiSystems/CustomScript-Shell?branch=develop)
[![Code Climate](https://codeclimate.com/github/QualiSystems/CustomScript-Shell/badges/gpa.svg)](https://codeclimate.com/github/QualiSystems/CustomScript-Shell)
[![Dependency Status](https://dependencyci.com/github/QualiSystems/CustomScript-Shell/badge)](https://dependencyci.com/github/QualiSystems/CustomScript-Shell)


# CustomScript-Shell 
This is an extended repo of the official Qualisystems configuration management package. 
Custom changes to driver and package have been added.

## Custom Param Overrides
The following configuration management parameters can be over-ridden by adding the following:
- REPO_URL
- REPO_USER
- REPO_PASSWORD (will be a plain text parameter)
- CONNECTION_METHOD

## Gitlab Support
- Gitlab links are supported, but require the URL to be in format of their REST api
- http://<SERVER_IP>/api/<API_VERSION>/projects/<PROJECT_ID>/repository/files/<PROJECT_PATH>/raw?ref=<GIT_BRANCH>
- example - http://10.160.7.7/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master

- The password field needs to be populated with gitlab access token, which will be sent along with request as header
- Gitlab docs - https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
- The "User" field can be left blank for gitlab auth. Only access token needed

## Changelog
- 25/06/2020 - Extending package to disable SSL Verification
- 25/12/2020 - Added Gitlab Support & Parameter Over-rides

## Links
* [Offline Package] (https://support.quali.com/hc/en-us/articles/231613247)
