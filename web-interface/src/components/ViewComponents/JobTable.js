import * as React from 'react';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import Container from '@mui/material/Container';

import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';

import FiberNewIcon from '@mui/icons-material/FiberNew';
import PendingIcon from '@mui/icons-material/Pending';
import LiveTvIcon from '@mui/icons-material/LiveTv';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CircularProgress from '@mui/material/CircularProgress';

import Timeline from 'react-visjs-timeline';

import VideoInformation from './VideoInformation';
import { capitalizeFirstLetter, constructTimelineData, convertHMS, unixTimeToFormatDate } from './Utility';

import '../../styles/JobTable.css';

let TimelineOptions = {
    width: '100%',
    height: '235px',
    showCurrentTime: false,
    zoomable: false,
    moveable: false,
}

const COLOR_CREATED = "#32893e";
const COLOR_PROCESSING = "#3273f1";
const COLOR_TRANSCODING = "#094684";
const COLOR_COMPLETED = "#26719c";

const TimelineGroups = [
    {
        id: 0,
        content: "Created",
        style: `background-color: ${COLOR_CREATED}; color: white;`,
    },
    {
        id: 1,
        content: "Processing",
        style: `background-color: ${COLOR_PROCESSING}; color: white;`,
    },
    {
        id: 2,
        content: "Transcoding",
        style: `background-color: ${COLOR_TRANSCODING}; color: white;`,
    },
    {
        id: 3,
        content: "Post-processing",
        style: `background-color: ${COLOR_COMPLETED}; color: white;`,
    },
];

// Returns a color for a <Chip /> depending on job status.
function statusStyle(jobStatus) {
    let fg = "white";
    let bg = "";

    switch (jobStatus) {
        case "created":
            bg = COLOR_CREATED;
            break;
        case "processing":
            bg = COLOR_PROCESSING;
            break;
        case "transcoding":
            bg = COLOR_TRANSCODING;
            break;
        case "completed":
            bg = COLOR_COMPLETED;
            break;
        default:
            bg = "primary";
            break;
    }

    return { backgroundColor: bg, color: fg };
}

// Returns an icon for a <Chip /> depending on job status.
function statusIcon(jobStatus) {
    switch (jobStatus) {
        case "created":
            return <FiberNewIcon />;
        case "processing":
            return <PendingIcon />;
        case "transcoding":
            return <LiveTvIcon />;
        case "completed":
            return <CheckCircleOutlineIcon />;
        default:
            return <FiberNewIcon />;
    }
}

class Row extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            open: false,
            videoInfo: {
                isLoaded: false,
            },
            VMAFData: {},
        };

        this.timelineRef = React.createRef();

        this.fetchVideoInformation = this.fetchVideoInformation.bind(this);
        this.fetchVMAFData = this.fetchVMAFData.bind(this);
        this.pollVMAFData = this.pollVMAFData.bind(this);
        this.renderVMAF = this.renderVMAF.bind(this);
        this.handleVMAFCompute = this.handleVMAFCompute.bind(this);
    }

    componentDidUpdate() {
        // If the state has changed we need to make sure that the timeline is
        // displaying all items across the entire timeline.
        this.timelineRef.current.$el.fit();

        //this.fetchVMAFData();
    }

    fetchVideoInformation() {
        fetch(`http://localhost:5000/api/video_info/${this.props.job.id}`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        ...this.state,
                        videoInfo: {
                            isLoaded: true,
                            error: false,
                            data: result,
                        }
                    });
                },
                // Note: it's important to handle errors here
                // instead of a catch() block so that we don't swallow
                // exceptions from actual bugs in components.
                (error) => {
                    this.setState({
                        ...this.state,
                        videoInfo: {
                            isLoaded: false,
                            error: true,
                            data: error,
                        }
                    });
                }
            )
    }

    fetchVMAFData() {
        fetch(`http://localhost:5000/api/vmaf_get/${this.props.job.id}`)
            .then(res => res.json())
            .then(result => {
                this.setState(result)
                if (!result.success) {
                    this.setState({
                        ...this.state,
                        VMAFData: {
                            isLoaded: true,
                            error: true,
                            message: result.payload.message,
                        }
                    });
                } else {

                    this.setState({
                        ...this.state,
                        VMAFData: {
                            isLoaded: true,
                            error: false,
                            data: result.payload.message,
                        }
                    });

                    // If we're not polling when the status is computing, start
                    // polling.
                    if (result.payload.message.status === "computing" && this.state.pollVMAFInterval === undefined) {
                        this.pollVMAFData();
                    }
                }
            }, error => {
                this.setState({
                    ...this.state,
                    VMAFData: {
                        isLoaded: true,
                        error: true,
                        message: error,
                    }
                });
            }
            )
    }

    pollVMAFData() {

        let pollIntervalID = setInterval(this.fetchVMAFData, 1000);

        this.setState({
            ...this.state,
            pollVMAFInterval: pollIntervalID,
        });
    }

    renderVMAF() {
        if (this.props.job.status !== "completed") {
            return;
        }

        if (this.state.VMAFData.hasOwnProperty("data") &&
            Object.keys(this.state.VMAFData).length !== 0) {

            let data = this.state.VMAFData.data;

            // Clear polling if result has been fetched.
            if (data.status === "completed" || data.status === "failed") {
                if (this.state.pollVMAFInterval) {

                    clearInterval(this.state.pollVMAFInterval);

                    this.setState({
                        ...this.state,
                        pollVMAFInterval: undefined,
                    });
                }
            }

            if (data.status === "computing") {
                return (
                    <Stack alignItems="center">
                        <CircularProgress />
                    </Stack>
                )
            } else if (data.status === "completed") {
                return (
                    <p style={{fontSize: "14pt"}}>VMAF score: {data.score}</p>
                )
            } else if (data.status === "failed") {
                return (
                    <p>Failed to compute VMAF score</p>
                )
            }

        } else if (this.state.VMAFData.isLoaded) {
            return (
                <Button
                    variant="contained"
                    style={{ width: "100%" }}
                    onClick={() => {
                        this.handleVMAFCompute();
                    }}>
                    Compute VMAF
                </Button>
            )
        }
    }

    handleVMAFCompute() {
        fetch(`http://localhost:5000/api/vmaf_compute/${this.props.job.id}`)
            .then(res => res.json())
            .then(
                (_) => {
                    this.pollVMAFData();
                    this.fetchVMAFData();
                },
                // Note: it's important to handle errors here
                // instead of a catch() block so that we don't swallow
                // exceptions from actual bugs in components.
                (_) => { }
            )
    }

    render() {
        return (
            <React.Fragment>
                <TableRow className={"JobRow " + (this.state.open ? "JobRowOpen" : "JobRowClosed")} sx={{ '& > *': { borderBottom: 'unset' } }} onClick={() => {

                    if (!this.state.open) {
                        this.fetchVideoInformation();
                        this.fetchVMAFData();
                    }

                    // Toggle open state.
                    this.setState({
                        ...this.state,
                        open: !this.state.open,
                    });
                }}>
                    <TableCell className="JobTableCell JobTableIdCell" component="th" scope="row">
                        {this.props.job.id}
                    </TableCell>
                    <TableCell className="JobTableCell" align="right">
                        <Stack spacing={1} alignItems="right">
                            <Chip label={capitalizeFirstLetter(this.props.job.status)} color="primary" icon={statusIcon(this.props.job.status)} variant="filled" sx={statusStyle(this.props.job.status)} />
                        </Stack>
                    </TableCell>
                    <TableCell className="JobTableCell" align="right">{this.props.job.video_location}</TableCell>
                    <TableCell className="JobTableCell" align="right">{this.props.job.output_location}</TableCell>
                    <TableCell className="JobTableCell" align="right">{this.props.job.shot_parameter}</TableCell>
                    <TableCell className="JobTableCell" align="right">{this.props.job.shot_length}</TableCell>
                    <TableCell className="JobTableCell" align="right">{this.props.type === "active"
                        ? unixTimeToFormatDate(this.props.job.time_created)
                        : convertHMS(this.props.job.time_completed - this.props.job.time_created)}</TableCell>
                    {this.props.type === "completed" ? <TableCell className="JobTableCell" align="right">{unixTimeToFormatDate(this.props.job.time_completed)}</TableCell> : ""}
                </TableRow>
                <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={8}>
                        <Collapse in={this.state.open} timeout="auto">
                            <Box sx={{ margin: 2 }}>
                                <Grid container rowSpacing={1} style={{ marginBottom: "20px" }}>
                                    <Grid item xs={10}>
                                        <VideoInformation videoInfo={this.state.videoInfo} />
                                    </Grid>

                                    <Grid item xs={2} style={{ textAlign: "center" }}>
                                        {this.renderVMAF()}
                                    </Grid>
                                </Grid>

                                <Timeline options={TimelineOptions} groups={TimelineGroups} items={constructTimelineData(this.props.job)} ref={this.timelineRef} />
                            </Box>
                        </Collapse>
                    </TableCell>
                </TableRow>
            </React.Fragment >
        );
    }
}

export default function JobTable(props) {
    return (
        <TableContainer component={Paper} className="JobTableContainer">
            <Table className="JobTable" stickyHeader aria-label="sticky collapsible table">
                <TableHead>
                    <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell align="right">Status</TableCell>
                        <TableCell align="right">Video</TableCell>
                        <TableCell align="right">Output Location</TableCell>
                        <TableCell align="right">Shot Parameter</TableCell>
                        <TableCell align="right">Min Shot Length</TableCell>
                        <TableCell align="right">{props.type === "active" ? "Created" : "Completed in (HH:MM:SS)"}</TableCell>
                        {props.type === "completed" ? <TableCell align="right">Completed</TableCell> : ""}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {props.jobs.map((job) => (
                        <Row key={job.id} job={job} type={props.type} />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}