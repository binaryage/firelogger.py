var item;

function onLoad() {
    item = window.arguments[0];

    document.getElementById("original").value = item.original;
    document.getElementById("rewrited").value = item.rewrited;
    onChange();
}

function onAccept() {
    item.original = document.getElementById("original").value;
    item.rewrited = document.getElementById("rewrited").value;
    window.arguments[1].saveChanges = true;
}

function onChange() {
    var hasOriginal = document.getElementById("original").value!="";
    var hasRewrited = document.getElementById("rewrited").value!="";
    document.documentElement.getButton("accept").disabled = !hasOriginal || !hasRewrited;
}