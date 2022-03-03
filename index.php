<html>
    <head>
        <title>CabalBot doc</title>
    </head>

    <body>
        <h1>Wikimedia CabalBot</h1>
        <p>A Sopel IRC bot plugin which provides a wide arrange of functions for Wikipedia/Wikimedia users. Current functions are:</p>
        <ul>
        <li>Report edits on a single page on any project with or without ping</li>
        <li>Globally watch a page in a specified namespace across all projects</li>
        <li>Report RC feed directly to any channel for any project</li>
        <li>Report Abuse Filter feed directly to any channel for any project</li>
        <li>Various IRC commands to assist with integration</li>
        </ul>
        <p>See the <a href="https://github.com/Operator873/CabalBot">repo</a></p>
        <h2>General Commands</h2>
        <p>The following commands are general commands the bot will respond to.</p>
        <p><code>!hush</code> / <code>!mute</code><br />
        Temporarily stop all commands to this channel. The bot will snitch who hushed it. Useful during mass actions.</p>
        <p><code>!speak</code><br />
        Resume reporting changes to the channel.</p>
        <p><code>!namespace {(int) OR (string)}</code><br />
        This is a limited dictionary query of some namespace numbers and names for reference. For example, to find the namespace number for &quot;User&quot; you would execute <code>!namespace User</code> which would return 2. Alternatively, you can also query to see what name space an integer is: <code>!namespace 2</code> which would return &quot;Article talk&quot;</p>
        <h2>Watch Commands</h2>
        <p>These commands instruct the bot to report changes to the specified page on the specified project. The ping setting will
        result in the bot mentioning the nick used to set the page to be watched.</p>
        <p><code>!watch add simplewiki Wikipedia:Vandalism in progress</code><br />
        This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org being reported in the current channel.</p>
        <p><code>watch del simplewiki Wikipedia:Vandalism in progress</code><br />
        This command would result in changes to Wikipedia:Vandalism in progress on simple.wikipedia.org no longer being reported in the current channel.</p>
        <p><code>!watch ping on enwiki Some Article</code><br />
        Add a ping to a watch report for the indicated page. In other words, the bot will specifically mention your IRC nick.</p>
        <p><code>!watch ping off enwiki Some Article</code><br />
        This will make the bot stop mentioning your nick during reports.</p>
        <h2>Global Watch Commands</h2>
        <p><code>!globalwatch {action} {namespaceID} {title}</code><br />
        General for of commands</p>
        <p><code>!globalwatch add 0 Main Page</code><br />
        Adds the page called &quot;Main Page&quot; in 0 namespace (Article) to global watch.</p>
        <p><code>!globalwatch del 3 Operator873</code><br />
        Stops following global changes to Operator873's talk page (3 is User talk)</p>
        <p><code>!globalwatch ping on 0 Main Page</code><br />
        Adds a ping (nick mention) to the global watch of &quot;Main Page&quot;</p>
        <p><code>!globalwatch ping off 0 Main Page</code><br />
        Removes the ping from the global watch of &quot;Main Page&quot;</p>
        <h2>Wikimedia Commands</h2>
        <p>These commands generally preformat a hyperlink to other Wikimedia tools by community memebers.</p>
        <p><code>!bullseye &lt;ip&gt;</code><br />
        Get a link for GeneralNotability's Bullseye tool for information on an IP address.</p>
        <p><code>!ca &lt;targetAccount&gt;</code><br />
        Generate a link to CentralAuth for the supplied Account.</p>
        <p><code>!contribs &lt;project&gt; &lt;target&gt;</code><br />
        Get a link to the contributions list for the target on the project provided. Target can be an account or an IP address. The project uses <code>meta</code>, <code>outreach</code>, <code>species</code> or <code>enwikibooks</code> format.</p>
        <p><code>!geo &lt;ip&gt;</code><br />
        Links to a geoip tool for the given IP address.</p>
        <p><code>!google &lt;search string&gt;</code><br />
        Returns a hyperlink for a Google search for the supplied string.</p>
        <p><code>!guc &lt;target&gt;</code><br />
        Generates a link to the guc tool for the supplied target, last hour only. Use <code>!gucall</code> for a complete listing.</p>
        <p><code>!ipqs &lt;ip&gt;</code><br />
        Link to IP Quality Score for the supplied IP address</p>
        <p><code>!proxy &lt;ip&gt;</code><br />
        Generates a link to SQL's ipcheck tool for the provided IP address.</p>
        <p><code>!rbf &lt;ip&gt;</code><br />
        Get a link to stwalkerster's Range Block Finder tool for the provided IP address.</p>
        <p><code>!stalk &lt;target&gt;</code><br />
        Creates a hyperlink to the stalktoy with the target as the object of the stalk.</p>
        <p><code>!stewardry &lt;target&gt;</code><br />
        Get a link for the stewardry tool for the supplied target.</p>
        <p><code>!urban &lt;string&gt;</code><br />
        Returns a link to the Urban Dictionary for the supplied term.</p>
        <p><code>!whois &lt;ip&gt;</code><br />
        Generates a link to the WHOIS tool with the supplied IP address.</p>
        <p><code>!xact &lt;target&gt;</code><br />
        Get a link to the cross wiki activity tool for the supplied target.</p>
        <p><code>!xtools &lt;project&gt; &lt;target&gt;</code><br />
        Get a link for Xtools on the project provided for the target provided.</p>
        <h2>Bot Admin Commands</h2>
        <p>These commands are only available to Bot Admins and are genereally considered sensitive.</p>
        <p><code>!feedadmin {add/del/list} &lt;ircAccount&gt;</code><br />
        Modify or read the current feedadmins for the channel the command was used in. The <code>list</code> option does not need a target,
        instead returning a list of current feedadmins in that channel.</p>
        <p><code>!watchstatus</code><br />
        Get the current status of the thread containing the EventListener</p>
        <p><code>!watchstart</code><br />
        If the thread is dead or has not been started, start EventListener into a new thread.</p>
        <p><code>!watchstop</code><br />
        Set the thread flag and gracefully stop the EventSource thread. Then delete it from bot memory.</p>
        <p><code>!addmember</code><br />
        Adds an IRC nick/Wikimedia account association for Global Sysops/Stewards</p>
        <p><code>!removemember</code><br />
        Removes an IRC nick/Wikimedia account association for Global Sysops/Stewards</p>
        <p><code>!setlang &lt;project&gt;</code><br />
        Informs the bot which project should be used in this channel for autolinking.</p>
        <p><code>!unsetlang</code><br />
        Removes the lang setting from the channel.</p>
        <p><code>!ignorenick &lt;IRCAccount&gt;</code><br />
        Tells the bot to not autolink <code>[[bracket wikilinks]]</code> from this IRC account. Useful for avoiding bot-bot interaction.</p>
        <p><code>!unnignorenick &lt;IRCAccount&gt;</code><br />
        Removes the IRC Account name from the ignored list and will resume generating autolinks.</p>
        <p><code>!restart</code> or <code>!restartbot &lt;reason&gt;</code><br />
        Orders the bot to fully restart with the provided reason (not required)</p>
        <p><code>!quit</code> or <code>!botdie &lt;reason&gt;</code><br />
        Orders the bot to terminate its process with the provided reason (not required)</p>
        <h2>Feed Admin Commands</h2>
        <p>Users that are trusted and set as a Feed Admin in a particular channel have access to the following commands.</p>
        <p><code>!abusefeed</code> or <code>!affeed {start/stop} &lt;project&gt;</code><br />
        The bot will report Abuse/Edit Filter activations on the indicated project</p>
        <p><code>!rcfeed {start/stop} &lt;project&gt;</code><br />
        The bot will report all activity for the provided project in the current channel. Very noisy. There is no AI or selective reporting with this command.</p>
        <p><code>!confirmedfeed {start/stop} &lt;project&gt;</code><br />
        The bot will report all edits and action performed by editors that are not confirmed.</p>
        <p><code>!oresfeed</code> or <code>!vandalfeed</code> or <code>!vandalismfeed {start/stop} &lt;project&gt;</code><br />
        Report edits that are likely vandalism via the ORES stream with a probability in the report.</p>
    </body>
</html>