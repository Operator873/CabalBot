![GitHub All Releases](https://img.shields.io/github/downloads/Operator873/SAM-for-desktop/releases)

# Wikimedia CabalBot #
A Sopel IRC Chat bot plugin which will allow you to watch pages locally or globally.

## Watch Commands ##

```!watch add simplewiki Wikipedia:Vandalism in progress```  
This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org being reported in the current channel.

```watch del simplewiki Wikipedia:Vandalism in progress```  
This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org no longer being reported in the current channel.

```!watch ping on enwiki Some Article```  
Add a ping to a watch report for the indicated page. In other words, the bot will specifically mention your IRC nick.

```!watch ping off enwiki Some Article```  
This will make the bot stop mentioning your nick during reports.

```!hush``` / ```!mute```  
Temporarily stop all commands to this channel. The bot will snitch who hushed it. Useful during mass actions.

```!speak```  
Resume reporting changes to the channel.

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

```!namespace {(int) OR (string)}```  
This is a limited dictionary query of some namespace numbers and names for reference. For example, to find the namespace number for "User" you would execute `!namespace User` which would return 2. Alternatively, you can also query to see what name space an integer is: `!namespace 2` which would return "Article talk"