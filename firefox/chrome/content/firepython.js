// This source contains copy&pasted various bits from Firebug sources.
// Some code comes from FirePHP project (http://www.firephp.org)
FBL.ns(function() {
    with(FBL) {
        const Cc = Components.classes;
        const Ci = Components.interfaces;

        const nsIPrefBranch = Ci.nsIPrefBranch;
        const nsIPrefBranch2 = Ci.nsIPrefBranch2;

        const firepythonPrefService = Cc["@mozilla.org/preferences-service;1"];
        const observerService = CCSV("@mozilla.org/observer-service;1", "nsIObserverService");

        const firepythonPrefs = firepythonPrefService.getService(nsIPrefBranch2);
        const firepythonURLs = {
            main: "http://github.com/woid/firepython",
        };
        const firepythonPrefDomain = "extensions.firepython";
        var firepythonOptionUpdateMap = {};

        if (Firebug.TraceModule) {
            Firebug.TraceModule.DBG_FIREPYTHON = false;
            var type = firepythonPrefs.getPrefType('extensions.firebug.DBG_FIREPYTHON');
            if (type != nsIPrefBranch.PREF_BOOL) try {
                firepythonPrefs.setBoolPref('extensions.firebug.DBG_FIREPYTHON', false);
            } catch(e) {}
        }
    
        function dbg() {
            if (FBTrace && FBTrace.DBG_FIREPYTHON) { 
                if (/FirePythonPanel/.test(arguments[0])) return;
                if (/FirePython.Record/.test(arguments[0])) return;
                FBTrace.sysout.apply(this, arguments);
            }
        }
    
        function capitalize(s) {
            return s.charAt(0).toUpperCase() + s.substring(1).toLowerCase();
        }
        
        FBL.$FIREPYTHON_STR = function(name)
        {
            return document.getElementById("strings_firepython").getString(name);
        };
        FBL.$FIREPYTHON_STRF = function(name, args)
        {
            return document.getElementById("strings_firepython").getFormattedString(name, args);
        };
    
        ////////////////////////////////////////////////////////////////////////
        var FirePythonEvent = function(type, data, icon) {
            this.type = type;
            this.data = data;
            this.icon = icon;
            this.expanded = false;
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Firebug.FirePythonContextMixin
        //
        Firebug.FirePythonContextMixin = {
            /////////////////////////////////////////////////////////////////////////////////////////
            extractHeaders: function(request) {
                var headers = [];
                var http = QI(request, Ci.nsIHttpChannel);
                http.visitResponseHeaders({
                    visitHeader: function(name, value) {
                        headers.push([name, value]);
                    }
                });
                return headers;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            pushRecord: function(url, info) {
                this.requestQueue.push([url, info]);
                if (this.processRequestQueueAutoFlushing) this.processRequestQueue();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            queueRequest: function(request) {
                dbg(">>>FirePythonContextMixin.queueRequest");
                var url = request.name;
                var headers = this.extractHeaders(request);
                var info = this.parseHeaders(headers);
                this.pushRecord(url, info);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            queueFile: function(file) {
                dbg(">>>FirePythonContextMixin.queueFile", file);
                this.pushRecord(file.href, this.parseHeaders(file.responseHeaders));
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            processRequestQueue: function() {
                dbg(">>>FirePythonContextMixin.processRequestQueue", this.requestQueue);
                for (var i=0; i<this.requestQueue.length; i++) {
                    var item = this.requestQueue[i];
                    this.processRequest(item[0], item[1]);
                }
                this.requestQueue = [];
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            parseHeaders: function(headers) {
                var buffer = "";
                var re = /^firepython/;
                var parseHeader = function(name, value) {
                    name = name.toLowerCase();
                    if (re.test(name)) { 
                        buffer+=value;
                    }
                }
                for (var index in headers) {
                    parseHeader(headers[index].name, headers[index].value);
                }
                // we use UTF-8 encoded JSON to exchange messages which are wrapped with base64
                buffer = Base64.decode(buffer);
                buffer = UTF8.decode(buffer);
                var packet = JSON.parse(buffer);
                return [packet];
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            processDataPacket: function(packet) {
                dbg(">>>FirePythonContextMixin.processDataPacket", packet);
                if (!packet) return;
                if (packet.logs) {
                    for (var i=0; i < packet.logs.length; i++) {
                        var log = packet.logs[i];
                        Firebug.FirePython.showLog(this, log, "log-"+log.level);
                    }
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            processRequest: function(url, packets) {
                dbg(">>>FirePythonContextMixin.processRequest ("+url+")", packets);
                for (var i=0; i < packets.length; i++) {
                    var packet = packets[i];
                    this.processDataPacket(packet);
                }
            }
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Firebug.FirePython
        //
        Firebug.FirePython = extend(Firebug.ActivableModule, {
            version: '0.1',
            currentPanel: null,

            /////////////////////////////////////////////////////////////////////////////////////////
            getPrefDomain: function() {
                return firepythonPrefDomain;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            checkFirebugVersion: function() {
                var version = Firebug.getVersion();
                if (!version) return false;
                var a = version.split('.');
                if (a.length<2) return false;
                // we want Firebug version 1.3+ (including alphas/betas and other weird stuff)
                return parseInt(a[0], 10)>=1 && parseInt(a[1], 10)>=3;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            versionCheck: function(context) {
                if (!this.checkFirebugVersion()) {
                    this.showMessage(context, "FirePython Firefox extension works best with Firebug 1.3 or higher. Please upgrade Firebug to the latest version.", "warning");
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            start: function() {
                dbg(">>>FirePython.start");
                observerService.addObserver(this, "http-on-modify-request", false);
                Firebug.NetMonitor.addListener(this);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            stop: function() {
                dbg(">>>FirePython.stop");
                observerService.removeObserver(this, "http-on-modify-request");
                Firebug.NetMonitor.removeListener(this);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            // Used for FB1.2 (>= b4)
            onLoad: function(context, file) {
                dbg(">>>FirePython.onLoad", [context, file]);
                this.mixinContext(context); // onLoad may be called before initContext, so we may need to mixin here
                context.queueFile(file);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            observe: function(subject, topic, data) {
                dbg(">>>FirePython.observe: "+topic);
                Firebug.ActivableModule.observe.apply(this, [subject, topic, data]);
                if (topic == "http-on-modify-request") {
                    var httpChannel = subject.QueryInterface(Ci.nsIHttpChannel);
                    // add FirePython/X.X.X to User-Agent header if not already there and firepython is enabled
                    // if firepython is not enabled remove header from request if it exists
                    // why X-FirePython? don't know, see https://developer.mozilla.org/En/Setting_HTTP_request_headers
                    if (httpChannel.getRequestHeader("User-Agent").match(/\sX-FirePython\/([\.|\d]*)\s?/) == null) {
                        httpChannel.setRequestHeader("User-Agent", httpChannel.getRequestHeader("User-Agent") + ' ' + "X-FirePython/" + this.version, false);
                    }
                }
                if (topic == "nsPref:changed") {
                    var parts = data.split(".");
                    var name = parts[parts.length-1];
                    var value = this.getPref(name);
                    this.updatePref(name, value);
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            updatePref: function(name, value) {
                dbg(">>>FirePython.updatePref: "+name+"->"+value);
                this.updatePanel();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            initialize: function() {
                dbg(">>>FirePython.initialize");
                this.panelName = 'FirePython';
                this.description = "Python logging tools for web developers";
                Firebug.ActivableModule.initialize.apply(this, arguments);
                firepythonPrefs.addObserver(this.getPrefDomain(), this, false);
                this.start();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            shutdown: function()
            {
                dbg(">>>FirePython.shutdown");
                firepythonPrefs.removeObserver(this.getPrefDomain(), this, false);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            initializeUI: function()
            {
                dbg(">>>FirePython.initializeUI");
                Firebug.ActivableModule.initializeUI.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onPanelActivate: function(context, init) {
                dbg(">>>FirePython.onPanelActivate");
                Firebug.ActivableModule.onPanelActivate.apply(this, arguments);
                if (!init) context.window.location.reload();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onPanelDeactivate: function(context, destroy, deactivatedPanelName) {
                dbg(">>>FirePython.onPanelDeactivate");
                Firebug.ActivableModule.onPanelDeactivate.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            mixinContext: function(context) {
                dbg(">>>FirePython.mixinContext");
                if (context.alreadyMixedWithFirePythonContext) return;
                context.alreadyMixedWithFirePythonContext = true;
                // mix-in FirePythonContextMixin into newly created context
                for (var p in Firebug.FirePythonContextMixin) context[p] = Firebug.FirePythonContextMixin[p];
                context.requestQueue = [];
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            initContext: function(context) {
                dbg(">>>FirePython.initContext");
                Firebug.ActivableModule.initContext.apply(this, arguments);
                this.mixinContext(context);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showContext: function(browser, context) {
                dbg(">>>FirePython.showContext");
                Firebug.ActivableModule.showContext.apply(this, arguments);
                this.versionCheck(context);
                context.processRequestQueue();
                context.processRequestQueueAutoFlushing = true;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            destroyContext: function(context) {
                dbg(">>>FirePython.destroyContext");
                Firebug.ActivableModule.destroyContext.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            reattachContext: function(browser, context) {
                dbg(">>>FirePython.reattachContext");
                Firebug.ActivableModule.reattachContext.apply(this, arguments);
                var panel = context.getPanel("FirePython");
                if (!panel) return;
                panel.applyCSS();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            loadedContext: function(context) {
                dbg(">>>FirePython.loadedContext");
                Firebug.ActivableModule.loadedContext.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            watchWindow: function(context, win) {
                dbg(">>>FirePython.watchWindow");
                Firebug.ActivableModule.watchWindow.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            unwatchWindow: function(context, win) {
                dbg(">>>FirePython.unwatchWindow");
                Firebug.ActivableModule.unwatchWindow.apply(this, arguments);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showPanel: function(browser, panel) {
                dbg(">>>FirePython.showPanel", panel);
                Firebug.ActivableModule.showPanel.apply(this, arguments);
                var isFirePython = panel && panel.name == "FirePython";
                if (isFirePython) {
                    if ((!Firebug.NetMonitor.isEnabled(panel.context) || !Firebug.Console.isEnabled(panel.context)) && !panel.context.fireGAEWarningShown) {
                        this.showMessage(panel.context, 'You must have the Firebug Console and Net panels enabled to use FirePython!', "warning");
                        panel.context.fireGAEWarningShown = true;
                    }
                    this.currentPanel = panel;
                    this.updatePanel();
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            updateFilterButtons: function(panel, states) {
                var browser = panel.context.browser;
                if (!browser) return;
                for (var s in states) {
                    var button = browser.chrome.$("fbFirePythonFilter"+capitalize(s)+"Button");
                    button.checked = !states[s];
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            updateFilterClasses: function(panel, states) {
                var node = panel.panelNode;
                for (var s in states) {
                    var classname = "filter-"+s;
                    removeClass(node, classname);
                    if (states[s]) setClass(node, classname);
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            updatePanel: function() {
                dbg(">>>FirePython.updatePanel", this.currentPanel);
                if (!this.currentPanel) return;
                var filterStates = this.loadFilterStates();
                this.updateFilterButtons(this.currentPanel, filterStates);
                this.updateFilterClasses(this.currentPanel, filterStates);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showLog: function(context, data, icon) {
                var event = new FirePythonEvent("log", data, icon);
                return this.publishEvent(context, event);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showException: function(context, data, icon) {
                var event = new FirePythonEvent("exception", data, icon);
                return this.publishEvent(context, event);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showMessage: function(context, text, icon) {
                if (!icon) icon = "info";
                var event = new FirePythonEvent("message", {
                    message: text,
                    time: this.getCurrentTime()
                }, icon);
                return this.publishEvent(context, event);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getCurrentTime: function() {
                var d = new Date();
                var h = d.getHours() + "";
                var m = d.getMinutes() + "";
                var s = d.getSeconds() + "";
                var x = d.getMilliseconds() + "";
                while (h.length < 2) h = "0" + h;
                while (m.length < 2) m = "0" + m;
                while (s.length < 2) s = "0" + s;
                while (x.length < 3) x = "0" + x;
                return h + ":" + m + ":" + s + "." + x;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            publishEvent: function(context, event) {
                if (!context) return;
                dbg(">>>FirePython.publishEvent", arguments);
                var panel = context.getPanel("FirePython");
                if (panel) panel.publish(event);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            loadExternalEditors: function()
            {
                const prefName = "externalEditors";
                const editorPrefNames = ["label", "executable", "cmdline", "image"];

                externalEditors = [];
                var list = Firebug.getPref(Firebug.prefDomain, prefName).split(",");
                for (var i = 0; i < list.length; ++i) {
                    var editorId = list[i];
                    if (!editorId || editorId == "")
                        continue;
                    var item = { id: editorId };
                    for (var j = 0; j < editorPrefNames.length; ++j) {
                        try {
                            item[editorPrefNames[j]] = Firebug.getPref(Firebug.prefDomain, prefName+"."+editorId+"."+editorPrefNames[j]);
                        } catch(exc) {}
                    }
                    if (item.label && item.executable) {
                        if (!item.image) item.image = getIconURLForFile(item.executable);
                        externalEditors.push(item);
                    }
                }
                return externalEditors;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            findPreferredEditor: function() {
                var preferredEditorId = this.getPref('preferredEditor');
                var editors = this.loadExternalEditors();
                var editor = null;
                for (var i=0; i<editors.length; i++) {
                    if (preferredEditorId == editors[i].id) return editors[i];
                }
                if (editors.length>0) return editors[0];
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            openSourceFile: function(path, line) {
                dbg(">>>FirePython.openSourceFile", [path, line]);
                if (!path) return;
                // TODO: replace paths for appspot
                // var editor = this.findPreferredEditor();
                // if (!editor) { 
                //     dbg(">>>no editor was found!");
                //     return;
                // }
                // var args = [];
                // if (editor.cmdline) {
                //     args = editor.cmdline.split(" ");
                //     for (var i=0; i<args.length; i++) {
                //         dbg("x", args[i]);
                //         args[i] = args[i].replace("%file", path);
                //         args[i] = args[i].replace("%line", line);
                //     }
                // }
                var editor = {
                    executable: "/bin/mate",
                };
                var args= ["-l", line, path];
                dbg(">>>Lauching "+editor.executable, args);
                try {
                    FBL.launchProgram(editor.executable, args);
                }
                catch (e) { dbg(">>>Launch exception", e); }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getPref: function(name) {
                dbg(">>>FirePython.getPref: "+name);
                var prefName = firepythonPrefDomain + "." + name;
    
                var type = firepythonPrefs.getPrefType(prefName);
                if (type == nsIPrefBranch.PREF_STRING)
                return firepythonPrefs.getCharPref(prefName);
                else if (type == nsIPrefBranch.PREF_INT)
                return firepythonPrefs.getIntPref(prefName);
                else if (type == nsIPrefBranch.PREF_BOOL)
                return firepythonPrefs.getBoolPref(prefName);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            setPref: function(name, value) {
                dbg(">>>FirePython.setPref: "+name+"->"+value);
                var prefName = firepythonPrefDomain + "." + name;
    
                var type = firepythonPrefs.getPrefType(prefName);
                if (type == nsIPrefBranch.PREF_STRING)
                firepythonPrefs.setCharPref(prefName, value);
                else if (type == nsIPrefBranch.PREF_INT)
                firepythonPrefs.setIntPref(prefName, value);
                else if (type == nsIPrefBranch.PREF_BOOL)
                firepythonPrefs.setBoolPref(prefName, value);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onOptionsShowing: function(popup) {
                Firebug.ActivableModule.onOptionsShowing.apply(this, arguments);
                for (var child = popup.firstChild; child; child = child.nextSibling) {
                    if (child.localName == "menuitem") {
                        var option = child.getAttribute("option");
                        if (option) {
                            var checked = false;
                            checked = this.getPref(option);
                            child.setAttribute("checked", checked);
                        }
                    }
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onVisitWebsite: function(which) {
                openNewTab(firepythonURLs[which]);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            loadFilterStates: function(states) {
                dbg(">>>FirePython.loadFilterStates", arguments);
                var states = ["debug", "info", "warning", "error", "critical"];
                var res = {};
                for (var i=0; i<states.length; i++) {
                    res[states[i]] = this.getPref("filter"+capitalize(states[i])+"Logs");
                }
                dbg(">>>Filter states", res);
                return res;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            storeFilterStates: function(states) {
                dbg(">>>FirePython.storeFilterStates", arguments);
                for (var s in states) {
                    this.setPref("filter"+capitalize(s)+"Logs", states[s]);
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onFilterLogs: function(what) {
                dbg(">>>FirePython.onFilterLogs", what);
                var states = this.loadFilterStates();
                states[what] = !states[what];
                this.storeFilterStates(states);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            openPermissions: function(event, context) {
                cancelEvent(event);
    
                var browserURI = FirebugChrome.getBrowserURI(context);
                var host = this.getHostForURI(browserURI);
    
                var params = {
                    permissionType: this.getPrefDomain(),
                    windowTitle: $FIREPYTHON_STR(this.panelName + ".Permissions"),
                    introText: $FIREPYTHON_STR(this.panelName + ".PermissionsIntro"),
                    blockVisible: true,
                    sessionVisible: false,
                    allowVisible: true,
                    prefilledHost: host,
                };
    
                openWindow("Browser:Permissions", "chrome://browser/content/preferences/permissions.xul", "", params);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getMenuLabel: function(option, location, shortened) {
                var label = "";
                var host = "";
    
                switch (option) {
                case "disable-site":
                    if (isSystemURL(location.spec))
                    label = "SystemPagesDisable";
                    else if (!getURIHost(location))
                    label = "LocalFilesDisable";
                    else
                    label = "HostDisable";
    
                    if (shortened)
                    return $FIREPYTHON_STR("panel.Disabled");
                    break;
    
                case "enable-site":
                    if (isSystemURL(location.spec))
                    label = "SystemPagesEnable";
                    else if (!getURIHost(location))
                    label = "LocalFilesEnable";
                    else
                    label = "HostEnable";
    
                    if (shortened)
                    return $FIREPYTHON_STR("panel.Enabled");
                    break;
    
                case "enable":
                    return $FIREPYTHON_STR("panel.Enabled");
    
                case "disable":
                    return $FIREPYTHON_STR("panel.Disabled");
                }
    
                if (!label)
                return null;
    
                label = this.panelName + "." + label;
                return $FIREPYTHON_STRF(label, [getURIHost(location)]);
            }
        });
    
        ////////////////////////////////////////////////////////////////////////
        // Firebug.FirePython.Record
        //
        Firebug.FirePython.Record = domplate(Firebug.Rep, {
            tagException: 
                DIV({ class: "rec-head closed $object|getIcon", _repObject: "$object"},
                    A({ class: "rec-title", onclick: "$onToggleDetails" },
                        IMG({ class: "rec-icon", src: "blank.gif"}),
                        SPAN({ class: "rec-date" }, "$object|getDate"),
                        SPAN({ class: "rec-uri" }, "$object|getCaption"),
                        SPAN({ class: "rec-info"}, "$object|getInfo")
                    ),
                    DIV({ class: "rec-details" })
                ),
    
            tagLog:
                DIV({ class: "rec-head $object|getIcon", _repObject: "$object" },
                    IMG({ class: "rec-icon", src: "blank.gif" }),
                    DIV({ class: "rec-date", onclick: "$onSourceNavigate" }, "$object|getDate"),
                    DIV({ class: "rec-uri" }, "$object|getCaption")
                ),

            tagMessage:
                DIV({ class: "rec-head $object|getIcon", _repObject: "$object" },
                    A({ class: "rec-title" },
                        IMG({ class: "rec-icon", src: "blank.gif" }),
                        SPAN({ class: "rec-uri" }, "$object|getCaption")
                    )
                ),
    
            /////////////////////////////////////////////////////////////////////////////////////////
            getCaption: function(event) {
                dbg(">>>FirePython.Record.getCaption", arguments);
                switch (event.type) {
                    case "message":
                    case "log":
                    case "exception": return event.data.message;
                }
                return "???";
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getIcon: function(event) {
                dbg(">>>FirePython.Record.getIcon", arguments);
                return event.icon;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getDate: function(event) {
                dbg(">>>FirePython.Record.getDate", arguments);
                return '[' + event.data.time + ']';
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getInfo: function(event) {
                dbg(">>>FirePython.Record.getInfo", arguments);
                var m = event.data;
                return "some info";
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            lookupEventObject: function(target) {
                var firepython = getAncestorByClass(target, "firepython-rec");
                var head = getChildByClass(firepython, "rec-head")
                var event = head.repObject;
                return event;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onSourceNavigate: function(e) {
                dbg(">>>FirePython.Record.onSourceNavigate", arguments);
                if (!isLeftClick(e)) return;
                var event = this.lookupEventObject(e.currentTarget);
                var path = event.data.pathname;
                var line = event.data.lineno;
                Firebug.FirePython.openSourceFile(path, line);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            onToggleDetails: function(e) {
                dbg(">>>FirePython.Record.onToggleDetails", arguments);
                if (!isLeftClick(e)) return;
                var event = this.lookupEventObject(e.currentTarget);
                var details = getChildByClass(row, "rec-details");

                toggleClass(row, "expanded");
                toggleClass(row, "closed");

                event.expanded = false;
                if (hasClass(row, "expanded"))
                {
                    event.expanded = true;
                    this.showEventDetails(event, details);
                }
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            showEventDetails: function(event, details) {
                var s = '';
                var m = event.data;
                details.innerHTML = "extra data";
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            supportsObject: function(object) {
                return object instanceof FirePythonEvent;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getRealObject: function(event, context) {
                return event.data;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getContextMenuItems: function(event) {
                return null;
            }
        });
    
        ////////////////////////////////////////////////////////////////////////
        // Firebug.FirePythonPanel
        //
        Firebug.FirePythonPanel = function() {}
        Firebug.FirePythonPanel.prototype = extend(Firebug.AblePanel, {
            name: "FirePython",
            title: "FirePython",
            searchable: true,
            editable: false,
    
            wasScrolledToBottom: true,
    
            /////////////////////////////////////////////////////////////////////////////////////////
            initialize: function() {
                dbg(">>>FirePythonPanel.initialize");
                Firebug.Panel.initialize.apply(this, arguments);
                this.applyCSS();
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            applyCSS: function() {
                dbg(">>>FirePythonPanel.applyCSS");
                this.applyPanelCSS("chrome://firepython/skin/panel.css");
                this.applyPanelCSS("chrome://firepython/skin/panel.css");
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            safeGetURI: function(browser) {
                try { return this.context.browser.currentURI; } catch(exc) {}
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            publish: function(event) {
                dbg(">>>FirePythonPanel.publish", event);
                event.root = this.append(event, "rec", null, null);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            clear: function() {
                dbg(">>>FirePythonPanel.clear");
                if (this.panelNode) clearNode(this.panelNode);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            show: function(state) {
                dbg(">>>FirePythonPanel.show", state);
                var enabled = Firebug.FirePython.isEnabled(this.context);
                this.showToolbarButtons("fbFirePythonButtons", true);
                this.showToolbarButtons("fbFirePythonFilters", enabled);
    
                if (enabled)
                    Firebug.ModuleManagerPage.hide(this);
                else
                    Firebug.ModuleManagerPage.show(this, Firebug.FirePython);
    
                if (this.wasScrolledToBottom) scrollToBottom(this.panelNode);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            hide: function() {
                dbg(">>>FirePythonPanel.hide");
                this.wasScrolledToBottom = isScrolledToBottom(this.panelNode);
                this.showToolbarButtons("fbFirePythonButtons", false);
                this.showToolbarButtons("fbFirePythonFilters", false);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getOptionsMenuItems: function() {
                dbg(">>>FirePythonPanel.getOptionsMenuItems");
                return null;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            search: function(text) {
                // make previously visible nodes invisible again
                if (this.matchSet) {
                    for (var i in this.matchSet)
                        removeClass(this.matchSet[i], "matched");
                }
                this.matchSet = [];

                if (!text) return;

                function findRow(node) { return getAncestorByClass(node, "firepython-rec"); }
                var search = new TextSearch(this.panelNode, findRow);

                var row = search.find(text);
                if (!row) return false;
                for (; row; row = search.findNext()) {
                    setClass(row, "matched");
                    this.matchSet.push(row);
                }
                return true;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getTopContainer: function() {
                return this.panelNode;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            createRow: function(rowName, className) {
                var elt = this.document.createElement("div");
                elt.className = rowName + (className ? " " + rowName + "-" + className: "");
                return elt;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            append: function(objects, className, rep) {
                dbg(">>>FirePythonPanel.append", arguments);
                var container = this.getTopContainer();
                var scrolledToBottom = isScrolledToBottom(this.panelNode);
                var row = this.createRow("firepython", className);
                this.appendObject.apply(this, [objects, row, rep]);
                container.appendChild(row);
                if (scrolledToBottom) scrollToBottom(this.panelNode);
                return row;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            appendObject: function(object, row, rep) {
                dbg(">>>FirePythonPanel.appendObject", arguments);
                var rep = rep ? rep: Firebug.getRep(object);
                var typeName = "tag"+capitalize(object.type);
                setClass(row, "kind-"+object.type);
                setClass(row, "subkind-"+object.icon);
                var res = rep[typeName].append({ object: object }, row);
                if (object.data.args && object.data.args.length>0) {
                    var dest = getChildByClass(row.childNodes[0], "rec-uri");
                    var ael = this.document.createElement('span');
                    setClass(ael, "rec-args");
                    var args = object.data.args;
                    var i = 0;
                    for (var a in args) {
                        var o = args[a];
                        var r = Firebug.getRep(o);
                        if (i) FirebugReps.Text.tag.append({object: ", "}, ael);
                        r.tag.append({object: o}, ael);
                        i = i + 1;
                    }
                    dest.appendChild(ael);
                }
                if (object.expanded) {
                    rep.onToggleDetails({ currentTarget: row.childNodes[0].childNodes[0] });
                }
                return res;
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            applyPanelCSS: function(url) {
                var links = FBL.getElementsBySelector(this.document, "link");
                for (var i=0; i < links.length; i++) {
                    var link = links[i];
                    if (link.getAttribute('href')==url) return; // already applied
                }
                var styleElement = this.document.createElement("link");
                styleElement.setAttribute("type", "text/css");
                styleElement.setAttribute("href", url);
                styleElement.setAttribute("rel", "stylesheet");
                var head = this.getHeadElement(this.document);
                if (head) head.appendChild(styleElement);
            },
            /////////////////////////////////////////////////////////////////////////////////////////
            getHeadElement: function(doc) {
                var heads = doc.getElementsByTagName("head");
                if (heads.length == 0) return doc.documentElement;
                return heads[0];
            }
        });
    
        Firebug.registerActivableModule(Firebug.FirePython);
        Firebug.registerRep(Firebug.FirePython.Record);
        Firebug.registerPanel(Firebug.FirePythonPanel);
    }
});
// close custom scope
