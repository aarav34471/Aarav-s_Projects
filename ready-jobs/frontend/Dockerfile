# pull official base image
FROM node:lts-slim

# set work directory
WORKDIR /srv/app/

# add to $PATH
ENV PATH /srv/app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm ci


# add app
COPY . ./

# Command to run the application
CMD ["npm", "start"]
