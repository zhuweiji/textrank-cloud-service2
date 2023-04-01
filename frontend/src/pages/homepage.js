import PropTypes from 'prop-types'

import React, { useRef, Component } from 'react'

import {
    Button, Typography, TextField, Box, Stack, Tabs, Tab, Paper, Pagination, Container,
    List, ListItem, ListItemText, Tooltip, IconButton
} from '@mui/material';

import CloudIcon from '@mui/icons-material/Cloud';
// import { FiberManualRecordIcon, SettingsInputAntennaIcon } from '@mui/icons-material';

import Grid from '@mui/material/Unstable_Grid2'; // Grid version 2
import { height } from '@mui/system';
import { styled } from '@mui/material/styles';

import { FileUploader } from "react-drag-drop-files";

import { HttpService } from '../services/api.js'
import { NetworkGraphComponent } from '../components/NetworkGraph.js'

class JobInProgress {
    constructor(task_id, task_type, completed) {
        this.task_id = task_id
        this.task_type = task_type
        this.completed = completed;
    }
    setComplete() {
        this.completed = true;
    }
}

const MLServices = {
    ImageRank: 'ImageRank',
    TextRank: 'TextRank',
    ImageTranscribe: 'ImageTransribe',

}


let data = {
    nodes: [
        { id: 'Myriel', group: 1 },
        { id: 'Napoleon', group: 1 },
        { id: 'ASD', group: 1 },
        { id: 'DAS', group: 1 },
        { id: 'BB', group: 1 },

    ],
    links: [
        { source: 'Myriel', target: 'Napoleon', value: 1 },
        { source: 'Napoleon', target: 'DAS', value: 1 },
        { source: 'Napoleon', target: 'Napoleon', value: 1 },
        { source: 'ASD', target: 'DAS', value: 1 },
        { source: 'BB', target: 'DAS', value: 1 },
        { source: 'ASD', target: 'BB', value: 1 },

    ]
}

const heartbeatInterval = 10000;

export function Homepage(props) {
    const acceptedImageFileTypes = ["JPG", "PNG"];

    const [imageTranscribeUploadedFiles, setImageTranscribeUploadedFiles] = React.useState([]);
    const [imageRankUploadedFiles, setImageRankUploadedFiles] = React.useState([]);


    const [jobsCreated, setJobsCreated] = React.useState([]);
    const [selectedJob, setSelectedJob] = React.useState(null); //the currently selected job in the 'jobs created' tab
    const [connectionAlive, setConnectionAlive] = React.useState(null);

    const [completedJobs, setCompletedJobs] = React.useState(new Map());
    const [idOfDisplayedJobResult, setIdOfDisplayedJobResult] = React.useState(null);

    const [modelSelectionTab, setModelSelectionTab] = React.useState(0);
    const [jobViewerTab, setJobViewerTab] = React.useState(0);

    const textFieldRef = useRef('') // a ref for the textField to enter ML input

    const handleUploadImageRankImage = (fileList) => {
        let files = Object.values(fileList);
        setImageRankUploadedFiles((old) => [...old, ...files]);
    }

    const handleUploadImage = (fileList) => {
        let files = Object.values(fileList);
        setImageTranscribeUploadedFiles((old) => [...old, ...files]);
    };

    const handleSubmitImageRankJob = async () => {
        let files = imageRankUploadedFiles;
        JobHandler.createNewImageRankJob(files, MLServices.ImageRank);
        setImageRankUploadedFiles([]);
    }

    const handleSubmitTextRankJob = async () => {
        let value = textFieldRef.current.value;
        JobHandler.createNewTextRankJob(value);
    }

    const handleSubmitImageTranscribeJob = async () => {
        let files = imageTranscribeUploadedFiles;
        JobHandler.createNewImageTranscribeJob(files);
        setImageTranscribeUploadedFiles([]);
    }

    class JobHandler {
        static numJobsCreated = 0;

        static async createNewImageRankJob(data) {
            const service = MLServices.ImageRank

            let displayedJob = new JobInProgress(`${this.numJobsCreated}`, service, false)
            this.putJobOnDisplayedQueue(displayedJob)

            let response = await HttpService.image_transcribe_service(data);
            let task_ids = response.task_id_list

            let hidden_jobs = task_ids.map((task_id) => new JobInProgress(task_id, service, false))
            let job_results = hidden_jobs.map(job => HttpService.get_job_result__long_poll(job.task_id, job))

            let values = await Promise.all(job_results)

            // convert the array of objects to a string 
            values = values.map(i => Object.values(i)[0]).join('|')

            this.handleJobCompletion({ 'data': values }, displayedJob)
        }

        static async createNewTextRankJob(data) {
            const service = MLServices.TextRank

            let response = await HttpService.text_rank_service(data);
            let task_id = response.task_id
            let job = new JobInProgress(task_id, service, false)
            this.putJobOnDisplayedQueue(job)
            this.updateJobUIOnBackendCompletion(job)
        }

        static async createNewImageTranscribeJob(data) {
            const service = MLServices.ImageTranscribe

            let response = await HttpService.image_transcribe_service(data);
            let task_ids = response.task_id_list
            let jobs = task_ids.map((task_id) => new JobInProgress(task_id, service, false))
            jobs.map(job => {
                this.putJobOnDisplayedQueue(job)
                this.updateJobUIOnBackendCompletion(job)
            })
        }

        static updateJobUIOnBackendCompletion(job) {
            HttpService.get_job_result__long_poll(job.task_id, job).then((job_result) => {
                this.handleJobCompletion(job_result, job)
            })
        }

        static putJobOnDisplayedQueue(job) {
            console.log(job)
            setJobsCreated((i) => [...i, job])
            if (jobsCreated.length === 0) {
                setSelectedJob(job);
            }
        }

        static handleJobCompletion = async (result, job) => {
            job.setComplete();
            setCompletedJobs(new Map(completedJobs.set(job.task_id, result)))
        }

        static displaySelectedJobResult = async () => {
            setIdOfDisplayedJobResult(selectedJob.task_id);
            setJobViewerTab(0);
        }
    }

    const backendConnectionDisplay = () => {
        let iconColor;
        let message;
        if (connectionAlive === null) {
            iconColor = 'disabled'
            message = "We're checking your connection now"
        } else if (!connectionAlive) {
            iconColor = '#b2102f'
            message = "The connection to the backend server is down currently"
        } else {
            iconColor = '#357a38'
            message = "You're connected!"
        }
        return <Tooltip title={message} >
            <IconButton>
                <CloudIcon sx={{ color: iconColor }} />
            </IconButton>
        </Tooltip >

    }

    React.useEffect(() => {
        async function heartbeatCheck() {
            let response = await HttpService.heartbeat();
            setConnectionAlive(response);
        }

        heartbeatCheck();
        setInterval(() => {
            heartbeatCheck();
        }, heartbeatInterval)
        return () => { }

    }, [])




    const ModelSelectionTabComponent = React.memo(() => {
        const handleTabChange = (event, newValue) => {
            setModelSelectionTab(newValue);
        };

        return <Box sx={{ height: '20rem' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={modelSelectionTab} onChange={handleTabChange} aria-label="basic tabs example">
                    <Tab label="ImageRank" {...a11yProps(0)} />
                    <Tab label="TextRank" {...a11yProps(1)} />
                    <Tab label="Image Transcription" {...a11yProps(2)} />
                </Tabs>
            </Box>

            <TabPanel value={modelSelectionTab} index={0}>
                <Typography pb={3} variant='h6'>ImageRank</Typography>
                <Typography >
                    Surface the most important images
                </Typography>

                <Typography pt={5} fontWeight='bold'>
                    Images Uploaded:
                </Typography>

                <Box sx={{ maxHeight: '10rem', overflowY: 'scroll', mb: 5 }}>
                    <List>
                        {imageRankUploadedFiles.map((i) => {
                            return <ListItem disablePadding key={i.name}>
                                <ListItemText primary={i.name} />
                            </ListItem >

                        })}

                    </List>

                </Box>

                <FileUploader name="file" handleChange={handleUploadImageRankImage} types={acceptedImageFileTypes} multiple />

                <Stack direction="row" justifyContent="flex-end" spacing={2}>
                    <Button variant='outlined' onClick={handleSubmitImageRankJob}>Submit</Button>
                </Stack>
            </TabPanel>

            <TabPanel value={modelSelectionTab} index={1}>
                <Typography pb={3} variant='h6'>TextRank Keyword Analysis</Typography>
                <Typography>
                    Cupidatat ad magna labore cillum non nulla anim do culpa velit ad qui incididunt.
                    Sunt fugiat laborum eu enim minim deserunt ipsum non exercitation laboris proident elit.
                </Typography>

                <Box mt={10}>
                    <TextField fullWidth multiline minRows={10} maxRows={10}
                        inputRef={textFieldRef}
                        label="Description" variant="outlined"
                    />

                    <Stack direction="row" justifyContent="end" pt={5}>
                        <Button variant="outlined" onClick={handleSubmitTextRankJob}>Submit</Button>
                    </Stack>
                </Box>

            </TabPanel>


            <TabPanel value={modelSelectionTab} index={2}>
                <Typography pb={3} variant='h6'>Some Image Model</Typography>
                <Typography >
                    Cupidatat ad magna labore cillum non nulla anim do culpa velit ad qui incididunt.
                    Sunt fugiat laborum eu enim minim deserunt ipsum non exercitation laboris proident elit.
                </Typography>

                <Typography pt={5} fontWeight='bold'>
                    Images Uploaded:
                </Typography>

                <Box sx={{ maxHeight: '10rem', overflowY: 'scroll', mb: 5 }}>
                    <List>
                        {imageTranscribeUploadedFiles.map((i) => {
                            return <ListItem disablePadding key={i.name}>
                                <ListItemText primary={i.name} />
                            </ListItem >

                        })}

                    </List>

                </Box>

                <FileUploader name="file" handleChange={handleUploadImage} types={acceptedImageFileTypes} multiple />

                <Stack direction="row" justifyContent="flex-end" spacing={2}>
                    <Button variant='outlined' onClick={handleSubmitImageTranscribeJob}>Submit</Button>
                </Stack>
            </TabPanel>
        </Box>
    })



    const JobViewerTabComponent = React.memo(() => {

        const handleTabChange2 = (event, newValue) => {
            setJobViewerTab(newValue);
        }

        return <>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={jobViewerTab} onChange={handleTabChange2} aria-label="basic tabs example">
                    <Tab label="Result Display" {...a11yProps(0)} />
                    <Tab label="Jobs Created" {...a11yProps(1)} />
                </Tabs>
            </Box>

            <TabPanel value={jobViewerTab} index={0}>
                <NetworkGraphComponent data={data} width={700} height={600} />
                {
                    completedJobs && completedJobs.get(idOfDisplayedJobResult) &&
                    Object.entries(completedJobs.get(idOfDisplayedJobResult)).map(([k, v]) => {
                        return <Typography key={k}>{k}: {v}</Typography>
                    })

                }

                {
                    (!completedJobs || !completedJobs.get(idOfDisplayedJobResult)) &&
                    <Stack direction="column" justifyContent="space-between" alignItems="center" spacing={2}>
                        <Typography>Data will be displayed here when you finish a job</Typography>
                    </Stack>

                }
            </TabPanel>


            <TabPanel value={jobViewerTab} index={1}>
                {
                    jobsCreated.length > 0 &&
                    <JobsCreatedPanel />
                }
                {
                    jobsCreated.length <= 0 &&
                    <Typography textAlign='center' fontStyle={'italic'} pt={5}>No jobs have been created yet.</Typography>

                }
            </TabPanel>
        </>

    })

    const JobsCreatedPanel = React.memo(() => {
        return <Box>
            <Pagination count={jobsCreated.length} onChange={(event, page) => { setSelectedJob(jobsCreated[page - 1]) }}> </Pagination>
            {
                selectedJob && <Box pt={5}>
                    <Typography textAlign='center'>Task ID: {selectedJob.task_id}</Typography>
                    <Typography textAlign='center'>task_type: {selectedJob.task_type}</Typography>
                    <Typography textAlign='center'>completed: {selectedJob.completed.toString()}</Typography>

                    <Stack direction="row" justifyContent="flex-end" spacing={2} mt={5}>
                        <Button variant="outlined" onClick={JobHandler.displaySelectedJobResult}>View Job Result</Button>
                    </Stack>
                </Box>
            }

        </Box>
    })

    return <>
        <Grid container spacing={5} pl={10} pt={10}>
            <Grid xs={6}>
                <ModelSelectionTabComponent />
            </Grid>
            <Grid xs={6}>
                <JobViewerTabComponent />
            </Grid>
        </Grid>

        <Box sx={{
            position: 'absolute',
            bottom: 20,
            right: 20
        }}>
            {backendConnectionDisplay()}
        </Box>

    </>

}

Homepage.propTypes = {}

// components for tabpanel 
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
                    <Typography component={'span'}>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
};

function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

// end components for tabpanel



