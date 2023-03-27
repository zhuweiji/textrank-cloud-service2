import PropTypes from 'prop-types'

import React, { useRef, Component } from 'react'

import {
    Button, Typography, TextField, Box, Stack, Tabs, Tab, Paper, Pagination, Container
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2'; // Grid version 2
import { height } from '@mui/system';
import { styled } from '@mui/material/styles';

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
    TextRank: 0,
}


export function Homepage(props) {
    const [jobsCreated, setJobsCreated] = React.useState([]);
    const [selectedJob, setSelectedJob] = React.useState(null); //the currently selected job in the 'jobs created' tab

    const [serviceSelected, setServiceSelected] = React.useState(MLServices.TextRank);

    const [completedJobs, setCompletedJobs] = React.useState(new Map());
    const [idOfDisplayedJobResult, setIdOfDisplayedJobResult] = React.useState(null);

    const handleChange = (event, newValue) => {
        setServiceSelected(newValue);
    };

    const textFieldRef = useRef('') // a ref for the textField to enter ML input

    const textFieldSubmit = async () => {
        let value = textFieldRef.current.value;
        createNewJob(value, serviceSelected);
    }

    const createNewJob = async (data, service) => {
        let resultPromise;
        console.log(service)
        if (service === MLServices.TextRank) {
            resultPromise = HttpService.text_rank_service(data)
        }

        let response = await resultPromise;
        let task_id = response.job_created
        console.log(response)

        let job = new JobInProgress(task_id, 'text_rank', false)
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

    function TabComponent() {
        return <Box sx={{ height: '20rem' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={serviceSelected} onChange={handleChange} aria-label="basic tabs example">
                    <Tab label="Model One" {...a11yProps(0)} />
                    <Tab label="Model Two" {...a11yProps(1)} />
                    <Tab label="Model Three" {...a11yProps(2)} />
                    <Tab label="Jobs Created" {...a11yProps(3)} />
                </Tabs>
            </Box>
            <TabPanel value={serviceSelected} index={MLServices.TextRank}>
                <Typography variant='h6'>TextRank Keyword Analysis</Typography>
                <Typography>
                    Cupidatat ad magna labore cillum non nulla anim do culpa velit ad qui incididunt.
                    Sunt fugiat laborum eu enim minim deserunt ipsum non exercitation laboris proident elit.
                </Typography>
            </TabPanel>
            <TabPanel value={serviceSelected} index={1}>
                Description Two
            </TabPanel>
            <TabPanel value={serviceSelected} index={2}>
                Description Three
            </TabPanel>
            <TabPanel value={serviceSelected} index={3}>
                {
                    jobsCreated.length > 0 &&
                    <Box>
                        <Pagination count={jobsCreated.length} onChange={(event, page) => setSelectedJob(jobsCreated[page - 1])}> </Pagination>
                        {
                            selectedJob && <Box pt={5}>
                                <Typography textAlign='center'>Task ID: {selectedJob.task_id}</Typography>
                                <Typography textAlign='center'>task_type: {selectedJob.task_type}</Typography>
                                <Typography textAlign='center'>completed: {selectedJob.completed.toString()}</Typography>

                                <Stack direction="row" justifyContent="flex-end" spacing={2}>
                                    <Button variant="outlined" onClick={displaySelectedJobResult}>Submit</Button>
                                </Stack>
                            </Box>
                        }

                    </Box>
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

                <Typography textAlign='center' variant='h3'>Hello!</Typography>

                <Box mt={10}>
                    <TextField fullWidth multiline minRows={10} maxRows={10}
                        inputRef={textFieldRef}
                        label="Description" variant="outlined"
                    />
                    <Stack direction="row" justifyContent="end" pt={5}>
                        {
                            Object.values(MLServices).includes(serviceSelected) &&
                            <Button variant="outlined" onClick={textFieldSubmit}>Submit</Button>
                        }
                    </Stack>
                </Box>


            </Grid>
            <Grid xs={6}>
                {
                    completedJobs && completedJobs.get(idOfDisplayedJobResult) &&
                    Object.entries(completedJobs.get(idOfDisplayedJobResult)).map(([k, v]) => {
                        return <Typography>{k}: {v}</Typography>
                    })

                }

            </Grid>
        </Grid>
    </>

}

Homepage.propTypes = {}

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

