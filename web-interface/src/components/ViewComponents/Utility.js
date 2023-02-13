
const constructTimelineData = job => {

    let data = [];

    let t_cr = unixTimeToDate(job.time_created);
    let t_pr = unixTimeToDate(job.time_processing);
    let t_tr = unixTimeToDate(job.time_transcoding);
    let t_co = unixTimeToDate(job.time_completed);

    data.push({ start: t_cr, group: 0, content: "Created" })

    if (job.time_processing !== 0) {
        data.push({
            start: t_cr, end: t_pr, group: 1,
            content: convertHMS(job.time_processing - job.time_created)
        })
    }

    if (job.time_transcoding !== 0) {
        data.push({
            start: t_pr, end: t_tr, group: 2,
            content: convertHMS(job.time_transcoding - job.time_processing)
        })
    }

    if (job.time_completed !== 0) {
        data.push({
            start: t_tr, end: t_co, group: 3,
            content: convertHMS(job.time_completed - job.time_transcoding)
        })

        // Uncomment the line below to add a point in time for when the job was
        // completed.
        //data.push({ start: t_co, group: 3, content: "Completed" })
    }

    return data;
}

function convertHMS(value) {
    const sec = parseInt(value, 10); // convert value to number if it's string
    let hours = Math.floor(sec / 3600); // get hours
    let minutes = Math.floor((sec - (hours * 3600)) / 60); // get minutes
    let seconds = sec - (hours * 3600) - (minutes * 60); //  get seconds
    // add 0 if value < 10; Example: 2 => 02
    if (hours < 10) { hours = "0" + hours; }
    if (minutes < 10) { minutes = "0" + minutes; }
    if (seconds < 10) { seconds = "0" + seconds; }
    return hours + ':' + minutes + ':' + seconds; // Return is HH : MM : SS
}

const unixTimeToFormatDate = unixTime => {

    let pt = (s) => ('0' + s).slice(-2);

    let date = new Date(unixTime * 1000);

    let fullDate = pt(date.getDate()) + "/"
        + pt((date.getMonth() + 1)) + "/"
        + date.getFullYear() + " "
        + pt(date.getHours()) + ":"
        + pt(date.getMinutes()) + ":"
        + pt(date.getSeconds());

    return fullDate;
};

const unixTimeToDate = unixTime => new Date(unixTime * 1000);

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function calculateFpsFromStr(fps_str) {
    let nums = fps_str.split("/");

    return Math.round(Number(nums[0]) / Number(nums[1]) * 100) / 100;
}

export {
    constructTimelineData,
    convertHMS,
    unixTimeToFormatDate,
    unixTimeToDate,
    capitalizeFirstLetter,
    calculateFpsFromStr,
}