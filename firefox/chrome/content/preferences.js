var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
const rewritesColumns = ["original", "rewrited"];

function openHelpLink(topic) {
    var url = "http://github.com/woid/firepython/wikis/"+topic;
    var args = window.arguments[0];
    var FBL = args.FBL;
    FBL.openNewTab(url);
}

function openPrefsHelp() {
  var helpTopic = document.getElementsByTagName("prefwindow")[0].currentPane.helpTopic;
  openHelpLink(helpTopic);
}

var mainPane = {
    _disablePasswordProtectionButton : null,

    /////////////////////////////////////////////////////////////////////////////////////////
    init: function() {
        var args = window.arguments[0];
        this._FBL = args.FBL;

        this._disablePasswordProtectionButton = document.getElementById("firepython-preferences-main-disable-password-protection");

        this.update();
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    disablePasswordProtection: function() {
        prefs.setCharPref("extensions.firepython.password", "");
        this.update();
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    update: function() {
        var that = this;
        setTimeout(function(){
            var enabled = prefs.getCharPref("extensions.firepython.password").trim()!="";
            that._disablePasswordProtectionButton.disabled = !enabled;
        }, 100);
    }
};

var rewritesPane = {
    _tree : null,
    _data : [],
    _removeButton : null,
    _changeButton : null,

    /////////////////////////////////////////////////////////////////////////////////////////
    getRewritesListNode: function() {
        return document.getElementById("firepython-preferences-rewrites-list");
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    init: function() {
        var args = window.arguments[0];
        this._FBL = args.FBL;
        this._prefName = "extensions.firepython.rewrites";

        this._removeButton = document.getElementById("firepython-preferences-rewrites-remove-rule");
        this._changeButton = document.getElementById("firepython-preferences-rewrites-change-rule");

        this._tree = this.getRewritesListNode();
        this._treeView =
        {
            data: this._data,
            selection: null,

            get rowCount() { return this.data.length; },
            getCellText: function(row, column)  {
                switch(column.id) {
                case "firepython-preferences-rewrites-list-original":
                    return this.data[row].original;
                case "firepython-preferences-rewrites-list-rewrited":
                    return this.data[row].rewrited;
                }
                return "";
            },
            setTree: function(treebox){ this.treebox = treebox; },
            isContainer: function(row) { return false; },
            isContainerOpen: function(row) { return false; },
            isContainerEmpty: function(row) { return false; },
            isSeparator: function(row) { return false; },
            isSorted: function() { return false; },
            getLevel: function(row) { return 0; },
            getImageSrc: function(row,column) { return null; },
            getRowProperties: function(row,props) {},
            getCellProperties: function(row,column,props) {},
            getColumnProperties: function(colid,column,props) {}
        };

        this._load();
        this._tree.view = this._treeView;
        
        this.update();
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    uninit: function() {
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    update: function() {
        var selection = this._tree.view.selection;
        this._removeButton.disabled = (selection.count != 1);
        this._changeButton.disabled = (selection.count != 1);
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    onSelectionChanged: function() {
        this.update();
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    addRewriteRule: function() {
        var item = { original: "", rewrited: "" };
        var result = {};
        openDialog("chrome://firepython/content/rewrite-rule.xul",  "_blank", "modal,centerscreen", item, result);
        if (result.saveChanges) {
            item.id = parseInt(Math.random()*1000000000);
            this._saveItem(item);

            this._loadItem(item);
            this._data.push(item);
            this._tree.view = this._treeView;

            var rules = [];
            try {
                var prefString = prefs.getCharPref(this._prefName)
                if (prefString) rules = prefString.split(",");
            } catch(e) { 
                this._FBL.ERROR(e); 
            }
            rules.push(item.id);
            prefs.setCharPref(this._prefName, rules.join(","));
        }
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    removeRewriteRule: function() {
        var selection = this._tree.view.selection;
        if (selection.count<1) return;
        var item = this._data[selection.currentIndex];
        this._data.splice(selection.currentIndex, 1);
        this._tree.view = this._treeView;
    
        try {
            var rules = prefs.getCharPref(this._prefName).split(",");
            this._FBL.remove(rules, item.id);
            prefs.setCharPref(this._prefName, rules.join(","));
            prefs.deleteBranch(this._prefName+"."+item.id);
        } catch(e) {
            this._FBL.ERROR(e);
        }
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    changeRewriteRule: function() {
        var selection = this._tree.view.selection;
        if (selection.count!=1) return;
        var item = this._data[selection.currentIndex];
        var result = {};
        openDialog("chrome://firepython/content/rewrite-rule.xul",  "_blank", "modal,centerscreen", item, result);
        if (result.saveChanges) {
            this._saveItem(item);
        }
        this._loadItem(item);
        this._tree.view = this._treeView;
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    _loadItem: function(item) {
        const prefName = this._prefName;
        for (var i=0; i<rewritesColumns.length; ++i) {
            try {
                item[rewritesColumns[i]] = prefs.getCharPref(prefName+"."+item.id+"."+rewritesColumns[i]);
            } catch(e) {}
        }
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    _saveItem: function(item) {
        const prefName = this._prefName;
        for (var i = 0; i<rewritesColumns.length; ++i) {
            try {
                var value = item[rewritesColumns[i]];
                if (value)
                    prefs.setCharPref(prefName+"."+item.id+"."+rewritesColumns[i], value);
                else
                    prefs.clearUserPref(prefName+"."+item.id+"."+rewritesColumns[i]);
            } catch(e) {}
        }
    },
    /////////////////////////////////////////////////////////////////////////////////////////
    _load: function() {
        try {
            var list = prefs.getCharPref(this._prefName).split(",");
            for (var i = 0; i < list.length; ++i)
            {
                var editorId = list[i].replace(/\s/g, "_");
                if ( !editorId )
                    continue;
                var item = { id: editorId };
                this._data.push(item);
                this._loadItem(item);
            }
        } catch(e) {
            this._FBL.ERROR(e);
        }
    }
};