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
    TextRank: 'TextRank',
    ImageModel: 'ImageModel',
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

    const [imageModelUploadedFiles, setImageModelUploadedFiles] = React.useState([]);

    const [jobsCreated, setJobsCreated] = React.useState([]);
    const [selectedJob, setSelectedJob] = React.useState(null); //the currently selected job in the 'jobs created' tab
    const [connectionAlive, setConnectionAlive] = React.useState(null);

    const [completedJobs, setCompletedJobs] = React.useState(new Map());
    const [idOfDisplayedJobResult, setIdOfDisplayedJobResult] = React.useState(null);

    const [modelSelectionTab, setModelSelectionTab] = React.useState(0);
    const [jobViewerTab, setJobViewerTab] = React.useState(0);

    const textFieldRef = useRef('') // a ref for the textField to enter ML input

    const handleUploadImage = (fileList) => {
        console.log(fileList)
        let files = Object.values(fileList);
        setImageModelUploadedFiles((old) => [...old, ...files]);
    };

    const handleSubmitTextRankJob = async () => {
        let value = textFieldRef.current.value;
        createNewJob(value, MLServices.TextRank);
    }

    const handleSubmitImageModelJob = async () => {
        let files = imageModelUploadedFiles;
        createNewJob(files, MLServices.ImageModel);
        setImageModelUploadedFiles([]);
    }

    const createNewJob = async (data, service) => {
        let resultPromise;
        if (service === MLServices.TextRank) {
            resultPromise = HttpService.text_rank_service(data)
        }
        else if (service === MLServices.ImageModel) {
            resultPromise = HttpService.image_transcribe_service(data)
        }

        let response = await resultPromise;
        let task_ids;

        if (response['task_id']) {
            task_ids = [response.task_id]
        } else if (response['task_id_list']) {
            task_ids = response.task_id_list
        } else {
            console.error(`unknown response for job start: ${response}}`)
            throw Error;
        }
        console.log(task_ids)
        let jobs = task_ids.map((task_id) => new JobInProgress(task_id, service, false))
        console.log(jobs)


        if (jobsCreated.length === 0) {
            setSelectedJob(jobs[0]);
        }

        setJobsCreated((i) => [...i, ...jobs])
        for (let job of jobs) {
            HttpService.get_job_result__long_poll(job.task_id, job).then((job_result) => {
                handleJobCompletion(job_result, job.task_id, job)
                console.log(job_result)
            })
        }
    }

    const handleJobCompletion = async (result, task_id, job) => {
        job.setComplete();
        setCompletedJobs(new Map(completedJobs.set(task_id, result)))
    }

    const displaySelectedJobResult = async () => {
        setIdOfDisplayedJobResult(selectedJob.task_id);
        setJobViewerTab(0);
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
                    <Tab label="Model One" {...a11yProps(0)} />
                    <Tab label="Model Two" {...a11yProps(1)} />
                    <Tab label="Model Three" {...a11yProps(2)} />
                </Tabs>
            </Box>


            <TabPanel value={modelSelectionTab} index={0}>
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


            <TabPanel value={modelSelectionTab} index={1}>
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
                        {imageModelUploadedFiles.map((i) => {
                            return <ListItem disablePadding key={i.name}>
                                <ListItemText primary={i.name} />
                            </ListItem >

                        })}

                    </List>

                </Box>

                <FileUploader name="file" handleChange={handleUploadImage} types={acceptedImageFileTypes} multiple />

                <Stack direction="row" justifyContent="flex-end" spacing={2}>
                    <Button variant='outlined' onClick={handleSubmitImageModelJob}>Submit</Button>
                </Stack>



            </TabPanel>


            <TabPanel value={modelSelectionTab} index={2}>
                Description Three
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
                        <Button variant="outlined" onClick={displaySelectedJobResult}>View Job Result</Button>
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



