import React, { Component } from 'react';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Slider from '@mui/material/Slider';
import CompressIcon from '@mui/icons-material/Compress';
import Button from '@mui/material/Button';
import InputIcon from '@mui/icons-material/Input';
import OutputIcon from '@mui/icons-material/Output';
import TimerIcon from '@mui/icons-material/Timer';
import Fade from '@mui/material/Fade';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';

export default class JobInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            inputPath: "",
            shotParameter: 0.3,
            outputPath: "",
            minLength: 0,
            set_alert: false,
            error_message: null,
            job_id: null
        };
        this.handleInput = this.handleInput.bind(this)
        this.handleShot = this.handleShot.bind(this)
        this.handleLength = this.handleLength.bind(this)
        this.handleOutput = this.handleOutput.bind(this)
        this.print_state = this.print_state.bind(this)
        this.upload_job = this.upload_job.bind(this)
        this.reset_inputs = this.reset_inputs(this)
    }


    print_state() {
        console.log(this.state)
    }

    reset_inputs() {
        this.setState({
            ...this.state,
            inputPath: "",
            shotParameter: 0.3,
            outputPath: "",
            minLength: 0,
        })
    }


    upload_job() {
        const data = {
            "type": "file_path",
            "shot_parameter": this.state.shotParameter,
            "shot_length": this.state.minLength,
            "video_location": this.state.inputPath,
            "output_location": this.state.outputPath
        };
        fetch(`http://localhost:5000/api/schedule_job`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success == false) {
                    this.setState({
                        ...this.state,
                        error_message: data.payload.message,
                        set_alert: true,
                        job_id: null
                    })
                    this.reset_inputs()
                    console.log(this.state)
                }
                else {
                    this.setState({
                        ...this.state,
                        error_message: null,
                        set_alert: false,
                        job_id: data.payload.job_id
                    })
                }
            })
            .catch((error) => {
                this.reset_inputs()
                console.log(this.state)
                this.setState({
                    error_message: error,
                    job_id: null,
                    set_alert: true
                })
            });
    }

    handleInput = (e) => {
        this.setState({ ...this.state, inputPath: e.target.value });
    };

    handleShot = (e) => {
        this.setState({ ...this.state, shotParameter: e.target.value })
    };

    handleLength = (e) => {
        e.target.value < 0 || e.target.value > 1000
            ? this.setState({ ...this.state, minLength: 0 })
            : this.setState({ ...this.state, minLength: Number(e.target.value) });
    };

    handleOutput = (e) => {
        this.setState({ ...this.state, outputPath: e.target.value });
    };

    render() {
        return (
            <Container
                component={Paper}
                className="JobUploadContainer"
                maxWidth="max"
                padding="50">
                <br />
                <h5>Video input</h5>
                <TextField
                    required
                    fullWidth={true}
                    id="file-path"
                    type="text"
                    label="Video to compress"
                    helperText="Absolute filepath"
                    variant="outlined"
                    value={this.state.inputPath}
                    onChange={this.handleInput}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <InputIcon />
                            </InputAdornment>
                        ),
                    }}
                />
                <br />
                <br />
                <h5>Shot Parameter</h5>
                <Slider
                    required
                    aria-label="Shot parameter"
                    value={this.state.shotParameter}
                    onChange={this.handleShot}
                    getAriaValueText={""}
                    valueLabelDisplay="on"
                    step={0.1}
                    marks
                    min={0}
                    max={1}
                    color='primary'
                />
                <h5>Minimum shot length</h5>
                <TextField
                    required
                    fullWidth={true}
                    value={this.state.minLength}
                    onChange={this.handleLength}
                    id="min-shot-len"
                    label="Minimum shot length"
                    type="number"
                    min="0"
                    max="1000"
                    helperText="In seconds 0-1000"
                    variant="outlined"
                    InputProps={{
                        inputMode: 'numeric',
                        type: 'number',
                        pattern: '[0-9]*',
                        startAdornment: (
                            <InputAdornment position="start">
                                <TimerIcon />
                            </InputAdornment>
                        ),
                    }}
                />
                <br />
                <br />
                <h5>Output folder</h5>
                <TextField
                    required
                    padding="300px"
                    fullWidth={true}
                    value={this.state.outputPath}
                    onChange={this.handleOutput}
                    id="outlined-basic"
                    label="Output"
                    type="text"
                    helperText="Absolute filepath"
                    variant="outlined"
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <OutputIcon />
                            </InputAdornment>
                        ),
                    }}
                />
                <br />
                <br />
                <Grid container spacing={2}>
                    <Grid item xs={4}>
                        <Button
                            variant='contained'
                            color='primary'
                            sx={{ width: 1 / 2 }}
                            size='medium'
                            endIcon={<CompressIcon />}
                            onClick={this.upload_job}
                            id="button"
                        >
                            Schedule Job
                        </Button>
                    </Grid>
                    <Grid item xs={8}>
                        <Fade in={this.state.set_alert} timeout={100} unmountOnExit>
                            <Alert
                                severity="error"
                                sx={{
                                    border: 1,
                                    width: 2 / 3
                                }}
                                variant="filled"
                            >
                                {this.state.error_message}</Alert>
                        </Fade>
                        <Fade in={this.state.job_id != null} timeout={100} unmountOnExit>
                            <Alert
                                severity="success"
                                sx={{
                                    border: 1,
                                    width: 2 / 3
                                }}
                                variant="filled"
                            >
                                Successfully scheduled job with ID '{this.state.job_id}'
                            </Alert>
                        </Fade>
                    </Grid>
                </Grid>
                <br />
                <br />
            </Container>
        );
    }
}
