
let getMaxLevel = (itemname) => {
    return parseInt(document.getElementById(itemname).getAttribute("data-max-level"));
}

let setProgressiveAcquiredLevel = (itemname, level) => {
    let targetLevel = Math.min(getMaxLevel(itemname), level);
    document.getElementById(itemname).setAttribute("class", "progressive-" + targetLevel);
}

let setAcquired = (itemname) => {
    let targetElement = document.getElementById(itemname);
    if (targetElement.tagName === "IMG") {
        targetElement.setAttribute("class", "acquired");
    } else {
        targetElement.setAttribute("class", "progressive-1");
    }
}

setAcquired("Ghost");
setAcquired("Shaped Blast (Siege Tank)");
setAcquired("Valkyrie");
setAcquired("Shockwave Missile Battery (Banshee)");
