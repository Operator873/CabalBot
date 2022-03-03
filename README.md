[![Github issues](https://img.shields.io/github/issues/Operator873/CabalBot?style=for-the-badge)](https://github.com/Operator873/CabalBot/issues)
[![Github forks](https://img.shields.io/github/forks/Operator873/CabalBot?style=for-the-badge)](https://github.com/Operator873/CabalBot/metwork)
[![Github stars](https://img.shields.io/github/stars/Operator873/CabalBot?style=for-the-badge)](https://github.com/Operator873/CabalBot/stargazers)
[![Github contributors](https://img.shields.io/github/contributors/Operator873/CabalBot?style=for-the-badge)](https://github.com/Operator873/CabalBot/graphs/contributors)

# Wikimedia CabalBot #
A Sopel IRC bot plugin which provides a wide arrange of functions for Wikipedia/Wikimedia users. Current functions are:
* Report edits on a single page on any project with or without ping
* Globally watch a page in a specified namespace across all projects
* Report RC feed directly to any channel for any project
* Report Abuse Filter feed directly to any channel for any project
* Various IRC commands to assist with integration

## General Commands ##
The following commands are general commands the bot will respond to.

```!hush``` / ```!mute```  
Temporarily stop all commands to this channel. The bot will snitch who hushed it. Useful during mass actions.

```!speak```  
Resume reporting changes to the channel.

```!namespace {(int) OR (string)}```  
This is a limited dictionary query of some namespace numbers and names for reference. For example, to find the namespace number for "User" you would execute `!namespace User` which would return 2. Alternatively, you can also query to see what name space an integer is: `!namespace 2` which would return "Article talk"

## Watch Commands ##
These commands instruct the bot to report changes to the specified page on the specified project. The ping setting will 
result in the bot mentioning the nick used to set the page to be watched.

```!watch add simplewiki Wikipedia:Vandalism in progress```  
This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org being reported in the current channel.

```watch del simplewiki Wikipedia:Vandalism in progress```  
This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org no longer being reported in the current channel.

```!watch ping on enwiki Some Article```  
Add a ping to a watch report for the indicated page. In other words, the bot will specifically mention your IRC nick.

```!watch ping off enwiki Some Article```  
This will make the bot stop mentioning your nick during reports.

## Global Watch Commands ##
```!globalwatch {action} {namespaceID} {title}```  
General for of commands

```!globalwatch add 0 Main Page```  
Adds the page called "Main Page" in 0 namespace (Article) to global watch.

```!globalwatch del 3 Operator873```  
Stops following global changes to Operator873's talk page (3 is User talk)

```!globalwatch ping on 0 Main Page```  
Adds a ping (nick mention) to the global watch of "Main Page"

```!globalwatch ping off 0 Main Page```  
Removes the ping from the global watch of "Main Page"

## Wikimedia Commands ##
These commands generally preformat a hyperlink to other Wikimedia tools by community memebers.

```!bullseye <ip>```  
Get a link for GeneralNotability's Bullseye tool for information on an IP address.

```!ca <targetAccount>```  
Generate a link to CentralAuth for the supplied Account.

```!contribs <project> <target>```  
Get a link to the contributions list for the target on the project provided. Target can be an account or an IP address. The project uses `meta`, `outreach`, `species` or `enwikibooks` format.

```!geo <ip>```  
Links to a geoip tool for the given IP address.

```!google <search string>```    
Returns a hyperlink for a Google search for the supplied string.

```!guc <target>```  
Generates a link to the guc tool for the supplied target, last hour only. Use `!gucall` for a complete listing.

```!ipqs <ip>```  
Link to IP Quality Score for the supplied IP address

```!proxy <ip>```  
Generates a link to SQL's ipcheck tool for the provided IP address.

```!rbf <ip>```  
Get a link to stwalkerster's Range Block Finder tool for the provided IP address.

```!stalk <target>```  
Creates a hyperlink to the stalktoy with the target as the object of the stalk.

```!stewardry <target>```  
Get a link for the stewardry tool for the supplied target.

```!urban <string>```  
Returns a link to the Urban Dictionary for the supplied term.

```!whois <ip>```  
Generates a link to the WHOIS tool with the supplied IP address.

```!xact <target>```  
Get a link to the cross wiki activity tool for the supplied target.

```!xtools <project> <target>```  
Get a link for Xtools on the project provided for the target provided.

## Bot Admin Commands ##
These commands are only available to Bot Admins and are genereally considered sensitive.

```!feedadmin {add/del/list} <ircAccount>```  
Modify or read the current feedadmins for the channel the command was used in. The `list` option does not need a target, 
instead returning a list of current feedadmins in that channel.

```!watchstatus```  
Get the current status of the thread containing the EventListener

```!watchstart```  
If the thread is dead or has not been started, start EventListener into a new thread.

```!watchstop```  
Set the thread flag and gracefully stop the EventSource thread. Then delete it from bot memory.

```!addmember```  
Adds an IRC nick/Wikimedia account association for Global Sysops/Stewards

```!removemember```   
Removes an IRC nick/Wikimedia account association for Global Sysops/Stewards

```!setlang <project>```  
Informs the bot which project should be used in this channel for autolinking.

```!unsetlang```    
Removes the lang setting from the channel.

```!ignorenick <IRCAccount>```  
Tells the bot to not autolink `[[bracket wikilinks]]` from this IRC account. Useful for avoiding bot-bot interaction.

```!unnignorenick <IRCAccount>```  
Removes the IRC Account name from the ignored list and will resume generating autolinks.

```!restart``` or ```!restartbot <reason>```  
Orders the bot to fully restart with the provided reason (not required)

```!quit``` or ```!botdie <reason>```  
Orders the bot to terminate its process with the provided reason (not required)

## Feed Admin Commands ##
Users that are trusted and set as a Feed Admin in a particular channel have access to the following commands.

```!abusefeed``` or ```!affeed {start/stop} <project>```  
The bot will report Abuse/Edit Filter activations on the indicated project

```!rcfeed {start/stop} <project>```  
The bot will report all activity for the provided project in the current channel. Very noisy. There is no AI or selective reporting with this command.

```!confirmedfeed {start/stop} <project>```  
The bot will report all edits and action performed by editors that are not confirmed.

```!oresfeed``` or ```!vandalfeed``` or ```!vandalismfeed {start/stop} <project>```  
Report edits that are likely vandalism via the ORES stream with a probability in the report.
