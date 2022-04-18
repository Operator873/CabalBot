import re
from sopel import plugin


@plugin.command("bullseye")
def bullseye(bot, trigger):
    # !bullseye <ip>
    target = trigger.group(3)
    bot.say("Bullseye: https://bullseye.toolforge.org/ip/" + target)


@plugin.command("ca")
def ca(bot, trigger):
    # !ca <target>
    target = trigger.group(2)
    bot.say("Meta CentralAuth https://meta.wikimedia.org/wiki/Special:CentralAuth/" + target.replace(' ', "_"))


@plugin.command("contribs")
def contribs(bot, trigger):
    # !contribs <project> <target>
    tricky_ones = ['commons', 'incubator', 'mediawiki', 'outreach', 'sources', 'species', 'wikidata', 'meta']
    try:
        project, target = trigger.group(2).split(" ", 1)
    except ValueError:
        bot.say("Something is missing... Syntax is !contribs <project> <target>")
        return
    target = target.replace(" ", "_")
    if project in tricky_ones:
        if project == "commons":
            bot.say("User contribs: https://commons.wikimedia.org/wiki/Special:Contribs/" + target)
        elif project == "incubator":
            bot.say("User contribs: https://incubator.wikimedia.org/wiki/Special:Contribs/" + target)
        elif project == "mediawiki":
            bot.say("User contribs: https://www.mediawiki.org/wiki/Special:Contribs/" + target)
        elif project == "outreach":
            bot.say("User contribs: https://outreach.wikimedia.org/wiki/Special:Contribs/" + target)
        elif project == "sources":
            bot.say("User contribs: https://www.wikisource.org/wiki/Special:Contribs/" + target)
        elif project == "species":
            bot.say("User contribs: https://species.wikimedia.org/wiki/Special:Contribs/" + target)
        elif project == "wikidata":
            bot.say("User contribs: https://www.wikidata.org/wiki/Special:Contribs/" + target)
        elif project == "meta":
            bot.say("User contribs: https://meta.wikimedia.org/wiki/Special:Contribs/" + target)
    else:
        try:
            lang, proj = re.split("w", project)
            lang = lang.replace("_", "-")
        except ValueError:
            lang = None

        target = target.replace(" ", "_")

        if lang is not None:
            if proj == "iki":
                bot.say("User contribs: https://" + lang + ".wikipedia.org/wiki/Special:Contribs/" + target)
            else:
                bot.say("User contribs: https://" + lang + ".w" + proj + ".org/wiki/Special:Contribs/" + target)

        else:
            bot.say("Hmm... I've tried and just can't figure out which project " + project + " is. I'm sorry.")


@plugin.command("geo")
def geo(bot, trigger):
    # !geo <ip>
    target = trigger.group(3)
    bot.say("Geolocate IP: https://whatismyipaddress.com/ip/1.1.1.1" + target)


@plugin.command("google")
def google(bot, trigger):
    # !google <query>
    target = trigger.group(2)
    bot.say("Google results: https://www.google.com/search?q=" + target.replace(" ", "_"))


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
    bot.say("Stalktoy: https://meta.toolforge.org/stalktoy/" + target.replace(" ", "_"))


@plugin.command("stewardry")
def stewardry(bot, trigger):
    # !stewardry <project>
    target = trigger.group(3)
    bot.say("Stewardry (sysop): https://meta.toolforge.org/stewardry/" + target.replace(" ", "_"))


@plugin.command("urban")
def urban(bot, trigger):
    # !urban <query>
    target = trigger.group(2)
    bot.say("Urban Dictionary lookup: https://www.urbandictionary.com/define.php?term=" + target.replace(" ", "_"))


@plugin.command("whois")
def whois(bot, trigger):
    # !whois <ip>
    target = trigger.group(3)
    bot.say("WHOIS lookup: https://whois-referral.toolforge.org/gateway.py?lookup=true&ip=" + target)


@plugin.command("xact")
def xact(bot, trigger):
    # !xact <user>
    target = trigger.group(2)
    bot.say("CrossActivity: https://meta2.toolforge.org/crossactivity/" + target.replace(" ", "_"))


@plugin.require_owner("This command has been disabled, as the tool is currently offline.")
@plugin.command("xcon")
def xcon(bot, trigger):
    # !xcon <user>
    target = trigger.group(2)
    bot.say("xContribs: https://erwin85.toolforge.org/xcontribs.php?user=" + target.replace(" ", "_"))


@plugin.command("xguc")
def xguc(bot, trigger):
    if trigger.group(2) != "":
        if re.search(r"\/", trigger.group(3)):
            bot.say("https://xtools.wmflabs.org/globalcontribs/ipr-" + trigger.group(3))
        else:
            bot.say("https://xtools.wmflabs.org/globalcontribs/" + trigger.group(3))
    else:
        bot.say("What is the target? !xguc <target>")


@plugin.command("xtools")
def xtools(bot, trigger):
    # !xtools <project> <target>
    tricky_ones = ['commons', 'incubator', 'mediawiki', 'outreach', 'sources', 'species', 'wikidata', 'meta']
    try:
        project, target = trigger.group(2).split(" ", 1)
    except ValueError:
        bot.say("Something is missing... Syntax is !xtools <project> <target>")
        return

    target = target.replace(" ", "_")
    if project in tricky_ones:
        if project == "commons":
            bot.say("XTools: https://xtools.wmflabs.org/ec/commons.wikimedia.org/" + target)
        elif project == "incubator":
            bot.say("XTools: https://xtools.wmflabs.org/ec/incubator.wikimedia.org/" + target)
        elif project == "mediawiki":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.mediawiki.org/" + target)
        elif project == "outreach":
            bot.say("XTools: https://xtools.wmflabs.org/ec/outreach.wikimedia.org/" + target)
        elif project == "sources":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.wikisource.org/" + target)
        elif project == "species":
            bot.say("XTools: https://xtools.wmflabs.org/ec/species.wikimedia.org/" + target)
        elif project == "wikidata":
            bot.say("XTools: https://xtools.wmflabs.org/ec/www.wikidata.org/" + target)
        elif project == "meta":
            bot.say("XTools: https://xtools.wmflabs.org/ec/meta.wikimedia.org/" + target)
    else:
        try:
            lang, proj = re.split("w", project)
            lang = lang.replace("_", "-")
        except ValueError:
            lang = None

        target = target.replace(" ", "_")

        if lang is not None:
            if proj == "iki":
                bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".wikipedia.org/" + target)
            else:
                bot.say("XTools: https://xtools.wmflabs.org/ec/" + lang + ".w" + proj + ".org/" + target)

        else:
            bot.say("Hmm... I've tried and just can't figure out which project " + project + " is. I'm sorry.")
