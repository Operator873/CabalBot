# This plugin will be used for bringing Wikimedia related commands to Bot873/GlobalSysBot
# and permit the retiring of CabalBot
import re
from sopel import plugin


@plugin.command("block")
def block(bot, trigger):
    # !block <project> <target>
    wiki = re.search("wiki$", trigger.group(3))
    wikibooks = re.search("wikibooks$", trigger.group(3))
    wikimedia = re.search("wikimedia$", trigger.group(3))
    wikinews = re.search("wikinews$", trigger.group(3))
    wikiquote = re.search("wikiquote$", trigger.group(3))
    wikisource = re.search("wikisource$", trigger.group(3))
    wikiversity = re.search("wikiversity$", trigger.group(3))
    wikivoyage = re.search("wikivoyage$", trigger.group(3))
    wiktionary = re.search("wiktionary$", trigger.group(3))

    count = len(trigger.group)
    i = 4
    target = ""

    while i < count:
        target += trigger.group(i)
        i = i + 1

    target = target.replace(" ", "_")

    if wiki:
        lang = re.split("wiki$", wiki.string)[0]
        lang = lang.replace("_", "-")
        if lang is "commons":
            bot.say("Sysop block link: https://commons.wikimedia.org/wiki/Special:Block/" + target)
        elif lang is "incubator":
            bot.say("Sysop block link: https://incubator.wikimedia.org/wiki/Special:Block/" + target)
        elif lang is "mediawiki":
            bot.say("Sysop block link: https://www.mediawiki.org/wiki/Special:Block/" + target)
        elif lang is "outreach":
            bot.say("Sysop block link: https://outreach.wikimedia.org/wiki/Special:Block/" + target)
        elif lang is "sources":
            bot.say("Sysop block link: https://www.wikisource.org/wiki/Special:Block/" + target)
        elif lang is "species":
            bot.say("Sysop block link: https://species.wikimedia.org/wiki/Special:Block/" + target)
        elif lang is "wikidata":
            bot.say("Sysop block link: https://www.wikidata.org/wiki/Special:Block/" + target)
        else:
            bot.say("Sysop block link: https://" + lang + ".wikipedia.org/wiki/Special:Block/" + target)
    elif wikibooks:
        lang = re.split("wikibooks$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikibooks.org/wiki/Special:Block/" + target)
    elif wikimedia:
        lang = re.split("wikimedia$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikimedia.org/wiki/Special:Block/" + target)
    elif wikinews:
        lang = re.split("wikinews$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikinews.org/wiki/Special:Block/" + target)
    elif wikiquote:
        lang = re.split("wikiquote$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikiquote.org/wiki/Special:Block/" + target)
    elif wikisource:
        lang = re.split("wikisource$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikisource.org/wiki/Special:Block/" + target)
    elif wikiversity:
        lang = re.split("wikiversity$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikiversity.org/wiki/Special:Block/" + target)
    elif wikivoyage:
        lang = re.split("wikivoyage$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wikivoyage.org/wiki/Special:Block/" + target)
    elif wiktionary:
        lang = re.split("wiktionary$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("Sysop block link: https://" + lang + ".wiktionary.org/wiki/Special:Block/" + target)
    else:
        bot.say("Invalid project name.")


@plugin.command("bullseye")
def bullseye(bot, trigger):
    # !bullseye <ip>
    target = trigger.group(3)
    bot.say("Bullseye: https://bullseye.toolforge.org/ip/" + target)


@plugin.command("ca")
def ca(bot, trigger):
    # !ca <target>
    target = trigger.group(2)
    bot.say("Meta CentralAuth https://meta.wikimedia.org/wiki/Special:CentralAuth/" + target)


@plugin.command("contribs")
def contribs(bot, trigger):
    # !contribs <project> <target>
    wiki = re.search("wiki$", trigger.group(3))
    wikibooks = re.search("wikibooks$", trigger.group(3))
    wikimedia = re.search("wikimedia$", trigger.group(3))
    wikinews = re.search("wikinews$", trigger.group(3))
    wikiquote = re.search("wikiquote$", trigger.group(3))
    wikisource = re.search("wikisource$", trigger.group(3))
    wikiversity = re.search("wikiversity$", trigger.group(3))
    wikivoyage = re.search("wikivoyage$", trigger.group(3))
    wiktionary = re.search("wiktionary$", trigger.group(3))

    count = len(trigger.group)
    i = 4
    target = ""

    while i < count:
        target += trigger.group(i)
        i = i + 1

    target = target.replace(" ", "_")

    if wiki:
        lang = re.split("wiki$", wiki.string)[0]
        lang = lang.replace("_", "-")
        if lang is "commons":
            bot.say("User contribs: https://commons.wikimedia.org/wiki/Special:Contribs/" + target)
        elif lang is "incubator":
            bot.say("User contribs: https://incubator.wikimedia.org/wiki/Special:Contribs/" + target)
        elif lang is "mediawiki":
            bot.say("User contribs: https://www.mediawiki.org/wiki/Special:Contribs/" + target)
        elif lang is "outreach":
            bot.say("User contribs: https://outreach.wikimedia.org/wiki/Special:Contribs/" + target)
        elif lang is "sources":
            bot.say("User contribs: https://www.wikisource.org/wiki/Special:Contribs/" + target)
        elif lang is "species":
            bot.say("User contribs: https://species.wikimedia.org/wiki/Special:Contribs/" + target)
        elif lang is "wikidata":
            bot.say("User contribs: https://www.wikidata.org/wiki/Special:Contribs/" + target)
        else:
            bot.say("User contribs: https://" + lang + ".wikipedia.org/wiki/Special:Contribs/" + target)
    elif wikibooks:
        lang = re.split("wikibooks$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikibooks.org/wiki/Special:Contribs/" + target)
    elif wikimedia:
        lang = re.split("wikimedia$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikimedia.org/wiki/Special:Contribs/" + target)
    elif wikinews:
        lang = re.split("wikinews$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikinews.org/wiki/Special:Contribs/" + target)
    elif wikiquote:
        lang = re.split("wikiquote$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikiquote.org/wiki/Special:Contribs/" + target)
    elif wikisource:
        lang = re.split("wikisource$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikisource.org/wiki/Special:Contribs/" + target)
    elif wikiversity:
        lang = re.split("wikiversity$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikiversity.org/wiki/Special:Contribs/" + target)
    elif wikivoyage:
        lang = re.split("wikivoyage$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wikivoyage.org/wiki/Special:Contribs/" + target)
    elif wiktionary:
        lang = re.split("wiktionary$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User contribs: https://" + lang + ".wiktionary.org/wiki/Special:Contribs/" + target)
    else:
        bot.say("Invalid project name.")


@plugin.command("geo")
def geo(bot, trigger):
    # !geo <ip>
    target = trigger.group(3)
    bot.say("Geolocate IP: https://whatismyipaddress.com/ip/1.1.1.1" + target)


@plugin.command("google")
def google(bot, trigger):
    # !google <query>
    target = trigger.group(2)
    bot.say("Google results: https://www.google.com/search?q=" + target)


@plugin.command("guc")
def guc(bot, trigger):
    # !guc <target>
    target = trigger.group(2)
    bot.say("Global contribs, last hour: https://tools.wmflabs.org/guc/?src=hr&by=date&user=" + target)


@plugin.command("gucall")
def gucall(bot, trigger):
    # !gucall <target>
    target = trigger.group(2)
    bot.say("Global contribs, all: https://tools.wmflabs.org/guc/?user=" + target)


@plugin.command("ipqs")
def ipqs(bot, trigger):
    # !ipqs <ip>
    target = trigger.group(3)
    bot.say("IP Quality Score: https://www.ipqualityscore.com/free-ip-lookup-proxy-vpn-test/lookup/" + target)


@plugin.command("link")
def link(bot, trigger):
    # !link <project> <target>
    wiki = re.search("wiki$", trigger.group(3))
    wikibooks = re.search("wikibooks$", trigger.group(3))
    wikimedia = re.search("wikimedia$", trigger.group(3))
    wikinews = re.search("wikinews$", trigger.group(3))
    wikiquote = re.search("wikiquote$", trigger.group(3))
    wikisource = re.search("wikisource$", trigger.group(3))
    wikiversity = re.search("wikiversity$", trigger.group(3))
    wikivoyage = re.search("wikivoyage$", trigger.group(3))
    wiktionary = re.search("wiktionary$", trigger.group(3))

    count = len(trigger.group)
    i = 4
    target = ""

    while i < count:
        target += trigger.group(i)
        i = i + 1

    target = target.replace(" ", "_")

    if wiki:
        lang = re.split("wiki$", wiki.string)[0]
        lang = lang.replace("_", "-")
        if lang is "commons":
            bot.say("https://commons.wikimedia.org/wiki/" + target)
        elif lang is "incubator":
            bot.say("https://incubator.wikimedia.org/wiki/" + target)
        elif lang is "mediawiki":
            bot.say("https://www.mediawiki.org/wiki/" + target)
        elif lang is "outreach":
            bot.say("https://outreach.wikimedia.org/wiki/" + target)
        elif lang is "sources":
            bot.say("https://www.wikisource.org/wiki/" + target)
        elif lang is "species":
            bot.say("https://species.wikimedia.org/wiki/" + target)
        elif lang is "wikidata":
            bot.say("https://www.wikidata.org/wiki/" + target)
        else:
            bot.say("https://" + lang + ".wikipedia.org/wiki/" + target)
    elif wikibooks:
        lang = re.split("wikibooks$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikibooks.org/wiki/" + target)
    elif wikimedia:
        lang = re.split("wikimedia$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikimedia.org/wiki/" + target)
    elif wikinews:
        lang = re.split("wikinews$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikinews.org/wiki/" + target)
    elif wikiquote:
        lang = re.split("wikiquote$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikiquote.org/wiki/" + target)
    elif wikisource:
        lang = re.split("wikisource$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikisource.org/wiki/" + target)
    elif wikiversity:
        lang = re.split("wikiversity$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikiversity.org/wiki/" + target)
    elif wikivoyage:
        lang = re.split("wikivoyage$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wikivoyage.org/wiki/" + target)
    elif wiktionary:
        lang = re.split("wiktionary$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("https://" + lang + ".wiktionary.org/wiki/" + target)
    else:
        bot.say("Invalid project name.")


@plugin.command("log")
def log(bot, trigger):
    # !log <project> <target>
    wiki = re.search("wiki$", trigger.group(3))
    wikibooks = re.search("wikibooks$", trigger.group(3))
    wikimedia = re.search("wikimedia$", trigger.group(3))
    wikinews = re.search("wikinews$", trigger.group(3))
    wikiquote = re.search("wikiquote$", trigger.group(3))
    wikisource = re.search("wikisource$", trigger.group(3))
    wikiversity = re.search("wikiversity$", trigger.group(3))
    wikivoyage = re.search("wikivoyage$", trigger.group(3))
    wiktionary = re.search("wiktionary$", trigger.group(3))

    count = len(trigger.group)
    i = 4
    target = ""

    while i < count:
        target += trigger.group(i)
        i = i + 1

    target = target.replace(" ", "_")

    if wiki:
        lang = re.split("wiki$", wiki.string)[0]
        lang = lang.replace("_", "-")
        if lang is "commons":
            bot.say("User logs: https://commons.wikimedia.org/wiki/Special:Log/" + target)
        elif lang is "incubator":
            bot.say("User logs: https://incubator.wikimedia.org/wiki/Special:Log/" + target)
        elif lang is "mediawiki":
            bot.say("User logs: https://www.mediawiki.org/wiki/Special:Log/" + target)
        elif lang is "outreach":
            bot.say("User logs: https://outreach.wikimedia.org/wiki/Special:Log/" + target)
        elif lang is "sources":
            bot.say("User logs: https://www.wikisource.org/wiki/Special:Log/" + target)
        elif lang is "species":
            bot.say("User logs: https://species.wikimedia.org/wiki/Special:Log/" + target)
        elif lang is "wikidata":
            bot.say("User logs: https://www.wikidata.org/wiki/Special:Log/" + target)
        else:
            bot.say("User logs: https://" + lang + ".wikipedia.org/wiki/Special:Log/" + target)
    elif wikibooks:
        lang = re.split("wikibooks$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikibooks.org/wiki/Special:Log/" + target)
    elif wikimedia:
        lang = re.split("wikimedia$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikimedia.org/wiki/Special:Log/" + target)
    elif wikinews:
        lang = re.split("wikinews$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikinews.org/wiki/Special:Log/" + target)
    elif wikiquote:
        lang = re.split("wikiquote$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikiquote.org/wiki/Special:Log/" + target)
    elif wikisource:
        lang = re.split("wikisource$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikisource.org/wiki/Special:Log/" + target)
    elif wikiversity:
        lang = re.split("wikiversity$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikiversity.org/wiki/Special:Log/" + target)
    elif wikivoyage:
        lang = re.split("wikivoyage$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wikivoyage.org/wiki/Special:Log/" + target)
    elif wiktionary:
        lang = re.split("wiktionary$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("User logs: https://" + lang + ".wiktionary.org/wiki/Special:Log/" + target)
    else:
        bot.say("Invalid project name.")


@plugin.command("proxy")
def proxy(bot, trigger):
    # !proxy <ip>
    target = trigger.group(3)
    bot.say("Proxy API Checker: https://ipcheck.toolforge.org/index.php?ip=" + target)


@plugin.command("rbf")
def rbf(bot, trigger):
    # !rbf <ip>
    target = trigger.group(3)
    bot.say("Range block finder: https://rangeblockfinder.toolforge.org/?excludelow&ip=" + target)


@plugin.command("stalk")
def stalk(bot, trigger):
    # !stalk <user>
    target = trigger.group(2)
    bot.say("Stalktoy: https://meta.toolforge.org/stalktoy/" + target)


@plugin.command("stewardry")
def stewardry(bot, trigger):
    # !stewardry <project>
    target = trigger.group(3)
    bot.say("Stewardry (sysop): https://meta.toolforge.org/stewardry/" + target)


@plugin.command("urban")
def urban(bot, trigger):
    # !urban <query>
    target = trigger.group(2)
    bot.say("Urban Dictionary lookup: https://www.urbandictionary.com/define.php?term=" + target)


@plugin.command("whois")
def whois(bot, trigger):
    # !whois <ip>
    target = trigger.group(3)
    bot.say("WHOIS lookup: https://whois-referral.toolforge.org/gateway.py?lookup=true&ip=" + target)


@plugin.command("xact")
def xact(bot, trigger):
    # !xact <user>
    target = trigger.group(2)
    bot.say("CrossActivity: https://meta2.toolforge.org/crossactivity/" + target)


@plugin.require_owner("This command has been disabled, as the tool is currently offline.")
@plugin.command("xcon")
def xcon(bot, trigger):
    # !xcon <user>
    target = trigger.group(2)
    bot.say("xContribs: https://erwin85.toolforge.org/xcontribs.php?user=" + target)


@plugin.command("xtools")
def xtools(bot, trigger):
    # !xtools <project> <target>
    wiki = re.search("wiki$", trigger.group(3))
    wikibooks = re.search("wikibooks$", trigger.group(3))
    wikimedia = re.search("wikimedia$", trigger.group(3))
    wikinews = re.search("wikinews$", trigger.group(3))
    wikiquote = re.search("wikiquote$", trigger.group(3))
    wikisource = re.search("wikisource$", trigger.group(3))
    wikiversity = re.search("wikiversity$", trigger.group(3))
    wikivoyage = re.search("wikivoyage$", trigger.group(3))
    wiktionary = re.search("wiktionary$", trigger.group(3))

    count = len(trigger.group)
    i = 4
    target = ""

    while i < count:
        target += trigger.group(i)
        i = i + 1

    target = target.replace(" ", "_")

    if wiki:
        lang = re.split("wiki$", wiki.string)[0]
        lang = lang.replace("_", "-")
        if lang is "commons":
            bot.say("XTools: https://xtools.wmflabs.org/ec/commons.wikimedia.org/" + target)
        elif lang is "incubator":
            bot.say("XTools: https://xtools.wmflabs.org/ec/incubator.wikimedia.org/" + target)
        elif lang is "mediawiki":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.mediawiki.org/" + target)
        elif lang is "outreach":
            bot.say("XTools: https://xtools.wmflabs.org/ec/outreach.wikimedia.org/" + target)
        elif lang is "sources":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.wikisource.org/" + target)
        elif lang is "species":
            bot.say("XTools: https://xtools.wmflabs.org/ec/species.wikimedia.org/" + target)
        elif lang is "wikidata":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.wikidata.org/" + target)
        else:
            bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikipedia.org/" + target)
    elif wikibooks:
        lang = re.split("wikibooks$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikibooks.org/" + target)
    elif wikimedia:
        lang = re.split("wikimedia$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikimedia.org/" + target)
    elif wikinews:
        lang = re.split("wikinews$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikinews.org/" + target)
    elif wikiquote:
        lang = re.split("wikiquote$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikiquote.org/" + target)
    elif wikisource:
        lang = re.split("wikisource$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikisource.org/" + target)
    elif wikiversity:
        lang = re.split("wikiversity$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikiversity.org/" + target)
    elif wikivoyage:
        lang = re.split("wikivoyage$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikivoyage.org/" + target)
    elif wiktionary:
        lang = re.split("wiktionary$", wiki.string)[0]
        lang = lang.replace("_", "-")
        bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wiktionary.org/" + target)
    else:
        bot.say("Invalid project name.")
