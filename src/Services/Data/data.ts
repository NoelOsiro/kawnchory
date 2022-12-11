import Photosnap from "../../assets/images/photosnap.png";
import Manage from "../../assets/images/manage.png";

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
    }
]