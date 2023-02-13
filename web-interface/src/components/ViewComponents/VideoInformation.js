

import { capitalizeFirstLetter, calculateFpsFromStr } from "./Utility";

function formatStreamData(stream) {

    let formatString;

    if (stream.codec_type === "video") {
        formatString = `Stream #${stream.index}: \
                        ${capitalizeFirstLetter(stream.codec_type)}: ${stream.codec_name}${stream.profile ? "(" + stream.profile + ")" : ""}, \
                        ${stream.pix_fmt} (${stream.field_order})\
                        [${stream.width}x${stream.height}, ${calculateFpsFromStr(stream.r_frame_rate)} fps]
                        `;

    } else if (stream.codec_type === "audio") {
        formatString = `Stream #${stream.index}: \
                        ${capitalizeFirstLetter(stream.codec_type)}: ${stream.codec_name}${stream.profile ? "(" + stream.profile + ")" : ""}, \
                        ${stream.sample_rate} Hz \
                        ${stream.channels} channels,
                        ${stream.sample_fmt} (${stream.bits_per_sample} bit) \
                        ${stream.bit_rate ? (stream.bit_rate / 1000) + " kb/s" : ""}
                        `;
    } else if (stream.codec_type === "subtitle") {
        formatString = `Stream #${stream.index}: \
                        ${capitalizeFirstLetter(stream.codec_type)}: ${stream.codec_name}, \
                        ${(stream.tags && stream.tags.title) ? stream.tags.title : ""}
                        `;
    } else {
        // Uncomment the line below to show other types of streams as well (attachment for example)
        //formatString = `Stream #${stream.index}: ${stream.codec_type}`;
    }

    return formatString;
}

function VideoInformation(props) {

    const videoInfo = props.videoInfo;

    if (!videoInfo || !videoInfo.isLoaded) {
        return <p></p>;
    } else if (Object.keys(videoInfo.data).length === 0) {
        // Display error message if the data object is empty.
        return <p>Could not load video information. The input file has probably been moved since job started.</p>;
    }

    return videoInfo.data.streams.map(stream => (
        <p className="streamInfo" key={stream.index}>{formatStreamData(stream)}</p>
    ));
}

export default VideoInformation;