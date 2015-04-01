# rtc2git
A tool made for migrating code from an existing [RTC] (https://jazz.net/products/rational-team-concert/) SCM repository into a Git repository
It uses the CLI of RTC to gather the required informations (You can find the CLI under the name "SCM Tools" [here] (https://jazz.net/downloads/rational-team-concert/releases/5.0.1?p=allDownloads))

## Prerequirements
<ul>
<li> RTC Version 5.0+ (Was tested using 5.0.1) </li> 
<li> RTC CLI --> (e.g Command "lscm help" should work in console) </li>
<li> Python 3 </li>
</ul>

## Usage
- Create a config file called "config.ini" and fill out the needed informations, use the supplied "config.ini.sample" as reference
- Collect the component history (for details please see the [wiki-entry] (https://github.com/WtfJoke/rtc2git/wiki/Getting-your-History-Files#how-i-get-the-complete-component-history))
- Execute migration.py


## How does it work?
<ol>
<li>It initalizes an empty git repository and clones it</li>
<li>In this repository, it loads a newly created rtc workspace based on your oldest stream</li>
<li>It iterates to a configured list of streams to determine the baseline of each component of this stream</li>
<li>For each baseline of this component a compare command will be executed</li>
<li>The result of the compare will be parsed to get to the necessary commit-informations (such as author, comment, date)</li>
<li>The change will be accepted in the workspace</li>
<li>The corresponding git command will be executed to do the same change in the git-repository</li>
</ol>


## Wiki
For more details [visit our wiki] (https://github.com/WtfJoke/rtc2git/wiki)
