import Photosnap from "../../assets/images/photosnap.png";
import Manage from "../../assets/images/manage.png";
import Account from "../../assets/images/account.png";
import MyHome from "../../assets/images/myhome.png";
import Shortly from "../../assets/images/shortly.png";
import EyeCam from "../../assets/images/eyecam.png";
import Loop from "../../assets/images/loop.png";
import Insure from "../../assets/images/insure.png";
import FaceIt from "../../assets/images/faceit.png";
import AirFilter from "../../assets/images/airfilter.png";
export interface JobData {
    logo:string;
    company_title:string;
    features:string[];
    job_title:string;
    job_tags:string[];
    status:string[];
  }
export const data:JobData[]=[
    {
        logo:Photosnap,
        company_title: "Photosnap",
        features:["NEW!","FEATURED"],
        job_title:"Senior Frontend Developer",
        job_tags:["Frontend","Senior","HTML","CSS","JavaScript"],
        status:["1d ago", "Full Time", "USA only"]
    },
    {
        logo:Manage,
        company_title: "Manage",
        features:["NEW!","FEATURED"],
        job_title:"Fullstack Developer",
        job_tags:["Fullstack","Midweight","Python","React"],
        status:["1d ago", "Part Time", "Remote"]
    },
    {
        logo:Account,
        company_title: "Account",
        features:["NEW!"],
        job_title:"Junior Frontend Developer",
        job_tags:["Frontend","Junior","React","Sass"," JavaScript"],
        status:["2d ago", "Part Time", "USA only"]
    },
    {
        logo:MyHome,
        company_title: "MyHome",
        features:[],
        job_title:"Junior Frontend Developer",
        job_tags:["Frontend","Junior","CSS"," JavaScript"],
        status:["5d ago", "Contract", "USA only"]
    },
    {
        logo:Loop,
        company_title: "Loop Studios",
        features:[],
        job_title:"Software Engineer",
        job_tags:["Fullstack","Midweight"," JavaScript","Sass", "Ruby"],
        status:["1w ago", "Full Time", "Wolrdwide"]
    },
    {
        logo:Shortly,
        company_title: "Shortly",
        features:[],
        job_title:"Junior Developer",
        job_tags:["Frontend","Junior", "HTML", "Sass", "JavaScript",],
        status:["2w ago", "Full Time", "Wolrdwide"]
    },
    {
        logo:Insure,
        company_title: "Insure",
        features:[],
        job_title:"Junior Frontend Developer",
        job_tags:["Frontend","Junior", "Vue", "JavaScript","Sass"],
        status:["2w ago", "Full Time", "USA only"]
    },
    {
        logo:EyeCam,
        company_title: "Eyecam co.",
        features:[],
        job_title:"Full Stack Engineer",
        job_tags:["Fullstack","Midweight", "Javascript", "Django","Python"],
        status:["3w ago", "Full Time", "Worldwide"]
    },
    {
        logo:AirFilter,
        company_title: "The Air Filter Company",
        features:[],
        job_title:"Front-end Dev",
        job_tags:["Frontend","Junior", "React","Sass", "JavaScript"],
        status:["1mo ago", "Part Time", "Worldwide"]
    }
    
]