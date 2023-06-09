import { BACKEND_URL } from '../settings.js'

export class HttpService {
    static async text_rank_service(text) {
        let url = `${BACKEND_URL}/text_rank`
        let data = {
            text: text
        }

        let response = await fetch(url,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(data)
            });

        if (response.status !== 200) {
            let error = await response.json()
            console.log(error)
            throw Error
        }

        let result = await response.json();
        return result;
    }

    static async sentence_extraction_service(str) {
        let url = `${BACKEND_URL}/sentence_extraction`
        let data = {
            text: str
        }

        let response = await fetch(url,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(data)
            });

        if (response.status !== 200) {
            let error = await response.json()
            console.log(error)
            throw Error
        }

        let result = await response.json();
        return result;
    }

    static async image_rank_w_sentences_service(str) {
        let url = `${BACKEND_URL}/create_image_rank_w_sentences_job`
        let data = {
            delimited_text: str
        }

        let response = await fetch(url,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(data)
            });

        if (response.status !== 200) {
            let error = await response.json()
            console.log(error)
            throw Error
        }

        let result = await response.json();
        return result;
    }

    static async image_transcribe_service(files) {
        let url = `${BACKEND_URL}/image_transcribe`

        let data = new FormData()
        for (const file of files) {
            data.append('images', file, file.name)
        }

        let response = await fetch(url,
            {
                method: 'POST',
                body: data
            });

        if (response.status !== 200) {
            let error = await response.json()
            console.log(error)
            throw Error
        }
        let result = await response.json();
        return result;
    }



    static async get_job_result__long_poll(task_id) {
        let url = `${BACKEND_URL}/check_task_result?`
        url += new URLSearchParams({
            task_id: task_id,
        })

        let response = await fetch(url,
            {
                method: 'GET',
                headers: { 'Content-Type': 'application/json', },
            });

        if (response.status === 502) {
            //connection timeout error - we are doing long-polling, so just make the request again
            return await this.get_job_result__long_poll(task_id);

        }
        if (response.status !== 200) {
            let error = await response.json()
            console.log(error)
            throw Error
        }
        let result = await response.json();
        return result;
    }

    static async heartbeat() {
        let url = `${BACKEND_URL.replace('/api', '')}/heartbeat`
        try {
            let response = await fetch(url,
                {
                    method: 'GET',
                });
            return response.status === 200;
        } catch (Error) {
            return false;
        }

    }


}

