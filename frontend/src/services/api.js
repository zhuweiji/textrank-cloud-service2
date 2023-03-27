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
            console.warn(response)
        }

        let result = await response.json();
        return result;
    }

    static async image_transcribe_service(image) {
        let url = `${BACKEND_URL}/image_transcribe`
        let data = {
            image: image
        }

        let response = await fetch(url,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(data)
            });

        if (response.status !== 200) {
            console.warn(response)

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
            console.warn(response)

        }
        let result = await response.json();
        return result;
    }


}

