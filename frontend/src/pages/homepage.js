import PropTypes from 'prop-types'

import React, { useRef, Component } from 'react'

import {
    Button, Typography, TextField, Box, Stack, Tabs, Tab, Paper, Pagination, Container,
    List, ListItem, ListItemText,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2'; // Grid version 2
import { height } from '@mui/system';
import { styled } from '@mui/material/styles';

import { FileUploader } from "react-drag-drop-files";

import { HttpService } from '../services/api.js'

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


export function Homepage(props) {
    const acceptedImageFileTypes = ["JPG", "PNG"];

    const [imageModelUploadedFiles, setImageModelUploadedFiles] = React.useState([]);

    const [jobsCreated, setJobsCreated] = React.useState([]);
    const [selectedJob, setSelectedJob] = React.useState(null); //the currently selected job in the 'jobs created' tab

    const [selectedTab, setSelectedTab] = React.useState(0);

    const [completedJobs, setCompletedJobs] = React.useState(new Map());
    const [idOfDisplayedJobResult, setIdOfDisplayedJobResult] = React.useState(null);

    const handleTabChange = (event, newValue) => {
        setSelectedTab(newValue);
    };

    const textFieldRef = useRef('') // a ref for the textField to enter ML input

    const handleSubmitTextRankJob = async () => {
        let value = textFieldRef.current.value;
        createNewJob(value, MLServices.TextRank);
    }

    const handleSubmitImageModelJob = async () => {
        let files = imageModelUploadedFiles;
        createNewJob(files, MLServices.ImageModel);

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
        let task_id = response.task_id

        console.log(response)

        let job = new JobInProgress(task_id, service, false)

        if (jobsCreated.length === 0) {
            setSelectedJob(job);
        }

        setJobsCreated((i) => [...i, job])

        let job_result = await HttpService.get_job_result__long_poll(task_id, job);
        handleJobCompletion(job_result, task_id, job)
    }

    const handleJobCompletion = async (result, task_id, job) => {
        job.setComplete();
        setCompletedJobs(new Map(completedJobs.set(task_id, result)))
    }

    const displaySelectedJobResult = async () => {
        setIdOfDisplayedJobResult(selectedJob.task_id);
        console.log(completedJobs);
        console.log(selectedJob.task_id)
        console.log(
            completedJobs.get(selectedJob.task_id)
        )
    }

    const handleUploadImage = (fileList) => {
        console.log(fileList)
        let files = Object.values(fileList);
        setImageModelUploadedFiles((old) => [...old, ...files]);
    };

    function JobsCreatedPanel() {
        return <Box>
            <Pagination count={jobsCreated.length} onChange={(event, page) => setSelectedJob(jobsCreated[page - 1])}> </Pagination>
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
    }


    function TabComponent() {
        return <Box sx={{ height: '20rem' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={selectedTab} onChange={handleTabChange} aria-label="basic tabs example">
                    <Tab label="Model One" {...a11yProps(0)} />
                    <Tab label="Model Two" {...a11yProps(1)} />
                    <Tab label="Model Three" {...a11yProps(2)} />
                    <Tab label="Jobs Created" {...a11yProps(3)} />
                </Tabs>
            </Box>


            <TabPanel value={selectedTab} index={0}>
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


            <TabPanel value={selectedTab} index={1}>
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


            <TabPanel value={selectedTab} index={2}>
                Description Three
            </TabPanel>


            <TabPanel value={selectedTab} index={3}>
                {
                    jobsCreated.length > 0 &&
                    <JobsCreatedPanel />
                }
                {
                    jobsCreated.length <= 0 &&
                    <Typography textAlign='center'>No jobs have been created yet.</Typography>

                }
            </TabPanel>


        </Box>
    }

    return <>
        <Grid container spacing={5} p={10}>
            <Grid xs={6}>

                <TabComponent />

            </Grid>
            <Grid xs={6}>
                {
                    completedJobs && completedJobs.get(idOfDisplayedJobResult) &&
                    Object.entries(completedJobs.get(idOfDisplayedJobResult)).map(([k, v]) => {
                        return <Typography>{k}: {v}</Typography>
                    })

                }

                {
                    (!completedJobs || !completedJobs.get(idOfDisplayedJobResult)) &&
                    <Stack direction="column" justifyContent="space-between" alignItems="center" spacing={2}>
                        <Typography>Stuff will be displayed here when you finish a job</Typography>
                    </Stack>

                }

            </Grid>
        </Grid>
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



