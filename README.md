[![Build Status](https://travis-ci.org/rtcTo/rtc2git.svg)](https://travis-ci.org/rtcTo/rtc2git)
[![Supported Versions](https://img.shields.io/badge/python-3.4%2C%203.5%2B-blue.svg)](https://travis-ci.org/rtcTo/rtc2git)
[![MIT License](https://img.shields.io/badge/license-MIT-orange.svg)](https://github.com/rtcTo/rtc2git/blob/develop/LICENSE)

# rtc2git

A tool made for migrating code from an existing [RTC](https://jazz.net/products/rational-team-concert/) SCM repository into a Git repository
It uses the CLI of RTC to gather the required information.

## Prerequirements

- RTC Server with Version 5.0+ (was tested using 5.0.1)
- **[SCM Tools](https://jazz.net/downloads/rational-team-concert/releases/5.0.1?p=allDownloads)** from IBM.  
   To avoid an account creation on the jazz.net site, you could use [bugmenot](http://bugmenot.com/).  
   Please make sure that your SCM Tools run in **English** (because we need to parse their output sometimes).  
   There is a wiki page on how to [configure RTC CLI](https://github.com/rtcTo/rtc2git/wiki/configure-RTC-CLI))
- Python 3.4+ (does not work with previous versions or with Python 2)

## Usage

- Create a config file called `config.ini` and fill out the needed information, use the supplied `config.ini.sample` or `config.ini.minimum.sample` as reference
- Execute `migration.py`


## How does it work?

1. It initalizes an empty git repository and clones it
2. In this repository, it loads a newly created (which will be set to the oldest baseline possible) or existing rtc workspace
3. The baseline of each component of a given stream is determined
4. For each baseline a compare command will be executed
5. The result of the compare will be parsed to get to the necessary commit-information (such as author, comment, date)
6. The change will be accepted in the workspace
7. The corresponding git command will be executed to do the same change in the git-repository


## Contribute

We welcome any feedback! :)

Feel free to report and/or fix [issues](https://github.com/rtcTo/rtc2git/issues) or create new pull requests

## Wiki

For more details [visit our wiki](https://github.com/rtcTo/rtc2git/wiki)
