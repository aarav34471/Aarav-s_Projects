import { axios } from 'axios';

//JUST A TEMPLATE 
export async function sendWelcomeEmail(name, email) {

        const serviceId = 'service_623rjzn';
        const templateId = 'template_5xs72zg';
        const publicKey = 'xw3SLy7tZOuNlT4zt';

        const data = {
            service_id: serviceId,
            template_id: templateId,
            user_id: publicKey,
            template_params: {
                name: name,
                email: email,
            }
        }

        try {
            const res = await axios.post("https://api.emailjs.com/api/v1.0/email/send", data);
            console.log(res.data);
        }

        catch (error) {
            console.log(error);
        }

    }



