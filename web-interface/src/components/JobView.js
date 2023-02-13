
import React, { Component } from 'react';

import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import Fade from '@mui/material/Fade';

import BasicAlert from './BasicAlert';

import Button from '@mui/material/Button';
import RefreshIcon from '@mui/icons-material/Refresh';

import JobTable from './ViewComponents/JobTable';
import '../styles/JobView.css';

function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    <Typography component={"span"}>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

export default class JobView extends Component {

    constructor(props) {
        super(props);

        this.state = {
            currentTab: 0,
            error: null,
            isLoaded: false,
            fetchAgainInterval: null,
            activeJobs: [],
            completedJobs: []
        };

        this.CountJobsOfStatus = this.CountJobsOfStatus.bind(this);
        this.reloadJobs = this.reloadJobs.bind(this);
        this.fetchJobData = this.fetchJobData.bind(this);
        this.tryFetchAgain = this.tryFetchAgain.bind(this);

        this.countDownIntervalFunction = this.countDownIntervalFunction.bind(this);
        this.handleTabChange = this.handleTabChange.bind(this);
    }

    CountJobsOfStatus(type) {
        let jobs =
            this.state.activeJobs.reduce((acc, job) => job.status === type ? acc + 1 : acc, 0);

        return jobs;
    }

    componentDidMount() {
        this.fetchJobData();

        // Poll job information every second instead of having to click
        // "Reload Jobs".
        this.reloadInterval = setInterval(this.reloadJobs, 1000);
    }

    componentWillUnmount() {
        clearInterval(this.realodInterval);
    }

    reloadJobs() {

        // If the jobs have already been loaded and the error is not null,
        // we'll reload the job data. This prevents multiple reloads at the same
        // time.
        if (this.state.isLoaded && this.state.error === null) {
            // Update isLoaded so that this cannot be called again until the jobs
            // have been loaded.
            this.setState({
                ...this.state,
                isLoaded: false,
            });

            this.fetchJobData();
        }
    }

    fetchJobData() {
        if (this.state.fetchCountdownInterval) {
            // If we're trying to fetch job data and the fetchCountdownInterval is
            // set, we'll clear it so that the countdown does not continue.
            clearInterval(this.state.fetchCountdownInterval);

            // Update the error message for fetching data.
            this.setState({
                ...this.state,
                fetchCountdownInterval: null,
                error: {
                    message: "Fetching data...",
                    type: "warning"
                }
            });
        }

        fetch(`http://localhost:5000/api/all_jobs`)
            .then(res => res.json())
            .then(
                result => {

                    // If the error field is defined, something has gone wrong
                    // in the backend.
                    if (result.error) {

                        this.setState({
                            ...this.state,
                            error: {
                                message: "Cannot fetch data from server. Please refresh the website. If the problem persists, contact the server administrator.",
                                type: "error"
                            }
                        })
                        return;
                    }

                    // Sort by time created.
                    result = result.sort((a, b) => a.time_created - b.time_created)

                    let activeJobs = [];
                    let completedJobs = [];

                    result.forEach(job => {
                        if (job.status === "completed") {
                            completedJobs.push(job);
                        } else {
                            activeJobs.push(job);
                        }
                    });

                    this.setState({
                        ...this.state,
                        isLoaded: true,
                        error: null,
                        activeJobs,
                        completedJobs
                    });
                },
                // Note: it's important to handle errors here instead of a
                // catch() block so that we don't swallow exceptions from actual
                // bugs in components.
                _ => {
                    this.setState({
                        ...this.state,
                        isLoaded: true,
                        error: {
                            message: "Failed to fetch jobs.",
                            type: "warning",
                            timeLeft: 5
                        },
                    });

                    this.tryFetchAgain();
                }
            )
    }

    countDownIntervalFunction() {
        this.setState({
            ...this.state,
            error: {
                message: `Failed to fetch jobs. Trying again in ${this.state.error.timeLeft} seconds.`,
                type: "warning",
                timeLeft: this.state.error.timeLeft - 1,
            },
        })
    }

    tryFetchAgain() {

        this.countDownIntervalFunction();
        const fetchCountdownInterval = setInterval(this.countDownIntervalFunction, 1000);

        setTimeout(this.fetchJobData, 5000);

        this.setState({
            ...this.state,
            fetchCountdownInterval
        });
    }

    handleTabChange(_, newValue) {
        this.setState({
            ...this.state,
            currentTab: newValue
        });
    }

    render() {
        return (
            <div className="JobView">

                <Fade in={!this.state.isLoaded} timeout={500} unmountOnExit className="fadeTopScreen">
                    <div>
                        <BasicAlert type="info" text="Loading job data..." />
                    </div>
                </Fade>

                <Fade in={this.state.error} timeout={500} unmountOnExit className="fadeTopScreen">
                    <div>
                        <BasicAlert type={this.state.error ? this.state.error.type : ""} text={this.state.error ? this.state.error.message : ""} />
                    </div>
                </Fade>

                <Box sx={{ width: '100%' }}>
                    <Button variant="contained" onClick={this.reloadJobs} startIcon={<RefreshIcon />} sx={{ marginBottom: "20px" }}>
                        Reload jobs
                    </Button>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <Tabs value={this.state.currentTab} onChange={this.handleTabChange} aria-label="basic tabs example">
                            <Tab label="Active Jobs" {...a11yProps(0)} />
                            <Tab label="Completed Jobs" {...a11yProps(1)} />
                        </Tabs>
                    </Box>

                    <TabPanel value={this.state.currentTab} index={0}>
                        <JobTable type="active" jobs={this.state.activeJobs} />
                    </TabPanel>

                    <TabPanel value={this.state.currentTab} index={1}>
                        <JobTable type="completed" jobs={this.state.completedJobs} />
                    </TabPanel>

                </Box>

            </div>
        )
    }

}