import PropTypes from 'prop-types'

import React, { useRef, Component } from 'react'

import {
    Button, Typography, TextField, Box, Stack, Tabs, Tab, Paper, Pagination, Container,
    List, ListItem, ListItemText, Tooltip, IconButton, Divider, LinearProgress
} from '@mui/material';

import CloudIcon from '@mui/icons-material/Cloud';
// import { FiberManualRecordIcon, SettingsInputAntennaIcon } from '@mui/icons-material';

import Grid from '@mui/material/Unstable_Grid2'; // Grid version 2
import { height } from '@mui/system';
import { styled } from '@mui/material/styles';

import { FileUploader } from "react-drag-drop-files";

import { Rainbow } from 'rainbowvis.js'

import { HttpService } from '../services/api.js'

import ReactDOM from 'react-dom';
import G6 from '@antv/g6';

import './homepage.css'


class JobInProgress {
    constructor(task_id, task_type, completed, progress) {
        this.task_id = task_id
        this.task_type = task_type
        this.completed = completed;
        this.progress = progress || 0;
    }
    setComplete() {
        this.completed = true;
    }
}


const MLServices = {
    ImageRank: 'ImageRank',
    TextRank: 'TextRank',
    SentenceExtraction: 'SentenceExtraction',
    ImageTranscribe: 'ImageTranscribe',
}

class JobDisplayedData {
    constructor(task_id, text, image, graph) {
        this.task_id = task_id
        this.text = text
        this.image = image
        this.graph = graph
    }
}


const heartbeatInterval = 10000;

export function Homepage(props) {
    const acceptedImageFileTypes = ["JPG", "PNG"];


    const [imageTranscribeUploadedFiles, setImageTranscribeUploadedFiles] = React.useState([]);  // temporarily store files that were uploaded but were not submitted for a job yet
    const [imageRankUploadedFiles, setImageRankUploadedFiles] = React.useState([]);              // temporarily store files that were uploaded but were not submitted for a job yet

    const [modelSelectionTab, setModelSelectionTab] = React.useState(0); // the tab number of the current machine learning model selected (lhs display)
    const [jobViewerTab, setJobViewerTab] = React.useState(0);           // the tab number of the right hand side display


    const [completedJobToResultMap, setCompletedJobToResultMap] = React.useState(new Map()); // map of completeted job taskid to the rendered output
    const [idOfDisplayedJobResult, setIdOfDisplayedJobResult] = React.useState(null);
    const [jobsCreated, setJobsCreated] = React.useState([]);
    const [selectedJob, setSelectedJob] = React.useState(null); //the currently selected job in the 'jobs created' tab
    const [connectionAlive, setConnectionAlive] = React.useState(null);

    const [displayedGraphData, setDisplayedGraphData] = React.useState({})  // the data used to render the displayed network graph
    const [displayedImageURL, setDisplayedImageURL] = React.useState(null);
    const [displayedTextResult, setDisplayedTextResult] = React.useState('');
    // const [jobMiscData, setJobMiscData] = React.useState({});

    const sentenceExtractiontextFieldRef = useRef('')
    const textFieldRef = useRef('') // a ref for the textField (textfield to enter ML input)

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

        setJobViewerTab(1);
    }

    const handleSubmitTextRankJob = async () => {
        let value = textFieldRef.current.value;
        JobHandler.createNewTextRankJob(value);

        setJobViewerTab(1);

    }

    const handleSubmitSentenceExtractionJob = () => {
        let value = sentenceExtractiontextFieldRef.current.value;
        JobHandler.createNewSentenceExtractionJob(value);

        setJobViewerTab(1);

    }

    const handleSubmitImageTranscribeJob = async () => {
        let files = imageTranscribeUploadedFiles;
        JobHandler.createNewImageTranscribeJob(files);
        setImageTranscribeUploadedFiles([]);

        setJobViewerTab(1);

    }

    //  this probably shouldnt be in a usestate but i had issues updating the variable whether it was static or global
    const [numJobsCreated, setNumJobsCreated] = React.useState(0);
    class JobHandler {

        static async createNewImageRankJob(data) {
            const service = MLServices.ImageRank

            // create a new job that the user can interact with that is only marked as completed when the underlying jobs to transcribe all the images are complete
            const displayedJobTaskId = `ImageRank ${numJobsCreated}`
            let displayedJob = new JobInProgress(displayedJobTaskId, service, false, 0);
            setNumJobsCreated((i) => i + 1)

            this.putJobOnDisplayedQueue(displayedJob)
            let response = await HttpService.image_transcribe_service(data);
            let task_ids = response.task_id_list

            // create hidden jobs that are not visible to the user
            let hidden_jobs = task_ids.map((task_id) => new JobInProgress(task_id, service, false))
            console.log(hidden_jobs)
            let job_results = hidden_jobs.map(job => this.getJobResult(job))
            console.log(job_results)

            let values = await Promise.all(job_results)
            if (values.length !== data.length) {
                throw Error('returned result of job has mismatching length')
            }
            displayedJob.setComplete()
            values = values.map((i, index) => `${i.result} ${index}`).join('|') // add a value to the end of the string to make t

            // use the sentence extraction pagerank method to give each image a score
            let node_ranking_response = await HttpService.image_rank_w_sentences_service(values);

            let node_ranking_job = new JobInProgress(node_ranking_response.task_id, service, false)
            let node_ranking_job_response = await this.getJobResult(node_ranking_job)
            let node_ranking_job_result = node_ranking_job_response.result

            let node_graph = node_ranking_job_result['keyword_extraction_result']
            let clusters = node_ranking_job_result['clusters']


            let graph = await createGraphStructureFromImageData(data, node_graph, clusters);

            console.log(graph)
            this.setResultsOfCompletedJob(displayedJobTaskId, null, null, graph)
        }

        static async createNewTextRankJob(data) {
            const service = MLServices.TextRank

            let response = await HttpService.text_rank_service(data);
            let task_id = response.task_id
            let job = new JobInProgress(task_id, service, false)
            this.putJobOnDisplayedQueue(job)
            let result = await this.getJobResult(job)

            let resultData = result.result
            let keyphraseAndScores = resultData.keyphrase_and_scores
            let keywordNodes = resultData.keyword_nodes

            let keyphrasesOnly = keyphraseAndScores.map(i => i[0]).slice(0, 6)

            let graphData = createGraphStructureFromTextRankData(keywordNodes);

            let filteredResultData = keywordNodes.slice(0, 10).map(i => i.name)
            let displayedOutputTextComponent = <>
                <Typography variant='h5' pt={3} pb={1} >
                    Key Phrases
                </Typography>

                <Typography whiteSpace='pre-wrap' pb={5} fontFamily='Roboto' >
                    {keyphrasesOnly.join('\n')}
                </Typography>

                <Divider />

                <Typography variant='h5' pt={5} pb={1} >
                    Keywords
                </Typography>

                <Typography whiteSpace='pre-wrap' pb={5} fontFamily='Roboto' >
                    {filteredResultData.join(', ')}
                </Typography>

                <Divider />



                <Typography variant='h5' pt={5} pb={2}>
                    Original Text
                </Typography>

                <Typography fontFamily='Roboto'>
                    {data}
                </Typography>
            </>




            this.setResultsOfCompletedJob(task_id, displayedOutputTextComponent, null, graphData)
        }

        static async createNewSentenceExtractionJob(data) {
            const service = MLServices.SentenceExtraction

            let response = await HttpService.sentence_extraction_service(data);
            let task_id = response.task_id
            let job = new JobInProgress(task_id, service, false)
            this.putJobOnDisplayedQueue(job)
            let result = await this.getJobResult(job)

            let resultData = result.result
            let resultModified = [];
            for (let obj of resultData) {
                obj['tooltip'] = obj.name
                obj['name'] = obj.name.slice(0, 10)
                resultModified.push(obj)
            }

            if (resultModified.length > 300) {
                resultModified = resultModified.slice(0, 300)
            }
            let graphData = createGraphStructureFromTextRankData(resultModified);


            let filteredResultData = resultData.slice(0, 5).map(i => i.tooltip)
            let displayedOutputText = filteredResultData.join('\n\n')

            let displayedOutputTextComponent = <Typography whiteSpace='pre-wrap'>
                {displayedOutputText}
            </Typography>


            this.setResultsOfCompletedJob(task_id, displayedOutputTextComponent, null, graphData)
        }



        static async createNewImageTranscribeJob(data) {
            const service = MLServices.ImageTranscribe

            let response = await HttpService.image_transcribe_service(data);
            let task_ids = response.task_id_list
            let jobs = task_ids.map((task_id) => new JobInProgress(task_id, service, false))


            jobs.forEach((job, index) => {
                this.putJobOnDisplayedQueue(job)

                let photoUrl = URL.createObjectURL(data[index]);

                // i have a feeling this is unintentionally blocking
                // the foreach loop shouldn't be blocked by waiting for a getJobResult
                let resultPromise = this.getJobResult(job)
                resultPromise.then((job_result) => {
                    let displayedOutputText = job_result['result']

                    let displayedOutputTextComponent = <Typography whiteSpace='pre-wrap'>
                        {displayedOutputText}
                    </Typography>

                    this.setResultsOfCompletedJob(job_result['task_id'], displayedOutputTextComponent, photoUrl, null)
                })
            })
        }

        static async getJobResult(job) {
            let result = await HttpService.get_job_result__long_poll(job.task_id, job);
            job.setComplete();
            return result;
        }

        static putJobOnDisplayedQueue(job) {
            setJobsCreated((i) => [...i, job])
            if (jobsCreated.length === 0) {
                setSelectedJob(job);
            }
        }
        static setResultsOfCompletedJob = (task_id, text, imageURL, graph) => {
            if (jobsCreated.filter((job) => job.task_id === task_id)) {
                let displayData = new JobDisplayedData(task_id, text, imageURL, graph);
                setCompletedJobToResultMap(new Map(completedJobToResultMap.set(task_id, displayData)))
            } else {
                console.warn(`tried to set the results of task_id ${task_id}} but that job was never created`)
            }
        }

        static displaySelectedJobResult = async () => {
            const task_id = selectedJob.task_id
            setIdOfDisplayedJobResult(selectedJob.task_id);
            setJobViewerTab(0);

            let result = completedJobToResultMap.get(task_id)
            if (!result) {
                console.warn(`tried to display ${task_id}} but that job doesn't have a result`)
                return
            }

            setDisplayedTextResult(result.text)
            setDisplayedImageURL(result.image)
            setDisplayedGraphData(result.graph)
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
                    <Tab label="Sentence Extraction" {...a11yProps(1)} />
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
                <Typography pb={3} variant='h6'>TextRank Keyword Extraction</Typography>
                <Typography>
                    Extracts keywords from user-entered text of any length.
                </Typography>
                <Typography>
                    This tool generates a list of relevant keywords and a network graph that visually represents the relationships between them.
                </Typography>
                <Typography pt={2}>
                    This feature may be valuable for professionals in fields such as research and writing, as well as anyone looking to gain a deeper understanding of their text.
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
                <Typography pb={3} variant='h6'>Sentence Extraction</Typography>
                <Typography>
                    Use TextRank to surface the most import sentences most representative of the entire text.
                </Typography>
                <Typography>
                    Use this to summarise research papers, news articles, or other blocks of text.
                </Typography>

                <Box mt={10}>
                    <TextField fullWidth multiline minRows={10} maxRows={10}
                        inputRef={sentenceExtractiontextFieldRef}
                        label="Description" variant="outlined"
                    />

                    <Stack direction="row" justifyContent="end" pt={5}>
                        <Button variant="outlined" onClick={handleSubmitSentenceExtractionJob}>Submit</Button>
                    </Stack>
                </Box>

            </TabPanel>


            <TabPanel value={modelSelectionTab} index={3}>
                <Typography pb={3} variant='h6'>Image Transcription</Typography>
                <Typography >
                    Transcribe your image as text, creating a summary of your image in textual format.
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
                {
                    displayedGraphData?.nodes?.length > 0 &&
                    <Box pb={5}>
                        <Typography variant='h6'>Graph</Typography>
                        <Divider />
                        <NetworkGraph2 data={displayedGraphData} />
                    </Box>
                }

                {
                    displayedImageURL &&
                    <Box pb={5}>
                        <Typography variant='h6'>Image</Typography>
                        <Divider />

                        <img src={displayedImageURL} width='75%' height='75%' />
                    </Box>
                }

                {
                    // completedJobToResultMap.get(idOfDisplayedJobResult)
                    displayedTextResult &&
                    <Box pb={5}>
                        <Typography variant='h6'>Text</Typography>
                        <Divider />
                        {displayedTextResult}
                        {/* <Typography whiteSpace='pre-wrap'>{displayedTextResult}</Typography> */}

                    </Box>

                }

                {
                    (!completedJobToResultMap || !completedJobToResultMap.get(idOfDisplayedJobResult)) &&
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
            <Pagination count={jobsCreated.length} page={jobsCreated.indexOf(selectedJob) + 1} onChange={(event, page) => { setSelectedJob(jobsCreated[page - 1]) }}> </Pagination>
            {
                selectedJob && <Box pt={5}>
                    <Typography textAlign='center'>Task ID: {selectedJob.task_id}</Typography>
                    <Typography textAlign='center'>task_type: {selectedJob.task_type}</Typography>
                    <Typography textAlign='center'>completed: {selectedJob.completed.toString()}</Typography>

                    <Box sx={{ width: '100%' }}>
                        {/* <LinearProgress variant="determinate" value={selectedJob.progress} /> */}
                    </Box>

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

// a function used to help redner the network graph
function refreshDraggedNodePosition(e) {
    const model = e.item.get('model');
    model.fx = e.x;
    model.fy = e.y;
}


function createGraphStructureFromTextRankData(data) {
    // function expects input in the following form:
    //  [
    // {id: str, name: str, score: str, connected: [ids]}
    // ]
    let resultObj = { 'nodes': [], 'edges': [] }

    let edgeMap = new Map()
    let meanScore = data.reduce((sum, i) => sum + parseFloat(i.score), 0) / data.length;

    // let rainbowColorObject = new Rainbow(); //an object that helps to create color gradients
    // rainbowColorObject.setNumberRange(1, data.length);
    // rainbowColorObject.setSpectrum('green', 'black');

    let colors = generateColor('#E1E5EE', '#31E981', data.length).map(i => '#' + i);
    console.log(colors)

    data.sort((i) => i.score)

    data.forEach((i, index) => {

        let node = {
            id: `${i.id}`,
            label: `${i.name.slice(0, 30)}`,
            score: `${i.score / meanScore}`,
            size: `${((i.score / meanScore) + 2) * 5}`,
            tooltip: `${i.tooltip}`,
            style: {
                fill: colors[index]
            }
        }
        i?.connected.forEach(other_id => edgeMap.set(i.id, other_id))
        resultObj['nodes'].push(node)
    })
    edgeMap.forEach((id1, id2) => {
        let edge = {
            id: `${id1}-${id2}`,
            source: `${id1}`,
            target: `${id2}`,
        }
        resultObj['edges'].push(edge)
    })
    return resultObj


}

// takes an array of files and a graph structure to create a antv G6 graph structure
async function createGraphStructureFromImageData(fileArray, nodeGraph, clusters) {
    let resultObj = { 'nodes': [], 'edges': [] }

    console.log(fileArray)
    console.log(nodeGraph)

    if (fileArray.length !== nodeGraph.length) {
        console.log(fileArray)
        console.log(nodeGraph)
        throw Error('mismatch in the lengths of the array of images and the corresponding array of nodes that is the result of the images passed through pagerank')
    }

    // generate clusters in the graph -- this code creates the combo objects that can contain several nodes 
    if (clusters !== undefined) {
        let combos = clusters.map((clusterArr, index) => {
            return { id: `combo${index}` }
        })
        console.log(combos)
        resultObj['combos'] = combos;
    }

    // create nodes
    fileArray.forEach((file, index) => {
        let url = URL.createObjectURL(file);
        let node = nodeGraph[index];


        let newNode = {
            'id': `${node.id}`,
            'tooltip': file.name,
            'transcription': node.name,
            'score': `${node.score}`,
            'size': node.score,
            'labelCfg': {
                position: 'bottom',
                offset: 10,
                fontSize: 5,
            },
            'icon': {
                show: true,
                img: url,
                width: 20,
                height: 20
            }
        }

        if (clusters !== undefined) {
            let clusterId = findIndicesOfValue(clusters, node.id).slice(0);
            if (clusterId) {
                newNode['comboId'] = `combo${clusterId}`
            }

        }
        resultObj['nodes'].push(newNode);
    })

    // create edges
    nodeGraph.forEach((node, index) => {
        let connectedIds = node.connected;
        connectedIds.forEach((otherId) => {
            let newEdge = {
                'source': `${node.id}`,
                'target': `${otherId}`
            }
            resultObj['edges'].push(newEdge);

        })

    })


    return resultObj;
}


function NetworkGraph2({ data }) {
    const ref = React.useRef(null);
    let graph = null;

    const tooltip = new G6.Tooltip({
        offsetX: 10,
        offsetY: 20,
        getContent(e) {
            const outDiv = document.createElement('div');
            outDiv.style.width = '180px';
            let tooltip_value = e.item.getModel().tooltip;
            if (tooltip_value === 'undefined') { // they set undefined as a string 
                tooltip_value = e.item.getModel().label
            }
            let score_value = e.item.getModel().score || ''
            let transcription_value = e.item.getModel().transcription || ''
            outDiv.innerHTML = `<p>${tooltip_value} ${transcription_value}</p><br><p>score: ${score_value}</p>`
            return outDiv
        },
        itemTypes: ['node']
    });

    React.useEffect(() => {
        if (!graph) {
            let graphProps = {
                container: ReactDOM.findDOMNode(ref.current),
                width: 800,
                height: 600,
                defaultNode: {
                    style: {
                        lineWidth: 0.1,
                        strokeOpacity: 0.5,
                    }
                },
                defaultEdge: {
                    // type: 'polyline',
                    style: {
                        lineWidth: 1,
                        strokeOpacity: 0.5,
                    }
                },
                defaultCombo: {
                    size: 50
                },
                modes: {
                    default: ['drag-canvas', 'zoom-canvas', 'drag-node', 'drag-combo', 'collapse-expand-combo',],
                },
                layout: {

                    type: 'force',
                    preventOverlap: true,
                    linkDistance: 100,
                    nodeStrength: d => d.score,

                    // type: 'radial',
                    // preventOverlap: true,
                    // nodeSize: 100,

                },
                plugins: [tooltip], // Use Tooltip plugin

            }

            if (data.combos) {
                graphProps['layout'] = {
                    type: 'comboForce',
                    center: [200, 200],     // The center of the graph by default
                    linkDistance: 100,         // Edge length
                    nodeStrength: 30,
                    edgeStrength: 0.1,
                    preventOverlap: true,

                }
            }
            graph = new G6.Graph(graphProps);
        }


        graph.data(data)
        graph.render();

        graph.on('afterlayout', e => {
            graph.fitView()
        })
    }, []);

    return <div ref={ref}></div>;
}

function findIndicesOfValue(arr, val) {
    var indices = [];
    for (var i = 0; i < arr.length; i++) {
        if (arr[i].indexOf(val) !== -1) {
            indices.push(i);
        }
    }
    return indices;
}


function hex(c) {
    var s = "0123456789abcdef";
    var i = parseInt(c);
    if (i == 0 || isNaN(c))
        return "00";
    i = Math.round(Math.min(Math.max(0, i), 255));
    return s.charAt((i - i % 16) / 16) + s.charAt(i % 16);
}

/* Convert an RGB triplet to a hex string */
function convertToHex(rgb) {
    return hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2]);
}

/* Remove '#' in color hex string */
function trim(s) { return (s.charAt(0) == '#') ? s.substring(1, 7) : s }

/* Convert a hex string to an RGB triplet */
function convertToRGB(hex) {
    var color = [];
    color[0] = parseInt((trim(hex)).substring(0, 2), 16);
    color[1] = parseInt((trim(hex)).substring(2, 4), 16);
    color[2] = parseInt((trim(hex)).substring(4, 6), 16);
    return color;
}

function generateColor(colorStart, colorEnd, colorCount) {

    // The beginning of your gradient
    var start = convertToRGB(colorStart);

    // The end of your gradient
    var end = convertToRGB(colorEnd);

    // The number of colors to compute
    var len = colorCount;

    //Alpha blending amount
    var alpha = 0.0;

    var saida = [];

    for (let i = 0; i < len; i++) {
        var c = [];
        alpha += (1.0 / len);

        c[0] = start[0] * alpha + (1 - alpha) * end[0];
        c[1] = start[1] * alpha + (1 - alpha) * end[1];
        c[2] = start[2] * alpha + (1 - alpha) * end[2];

        saida.push(convertToHex(c));

    }

    return saida;

}