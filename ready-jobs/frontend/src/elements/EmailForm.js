import axios from 'axios';

export async function sendWelcomeEmail(name, email) {

        const serviceId = process.env.REACT_APP_EMAILJS_SERVICE_ID;
        const templateId = process.env.REACT_APP_EMAILJS_WELCOME_TEMPLATE_ID;
        const publicKey = process.env.REACT_APP_EMAILJS_PUBLIC_KEY;

        if (!serviceId || !templateId || !publicKey) {
            return;
        }

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

