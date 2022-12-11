import React from 'react'
import { CardRow, CardContent, 
  CardLogo, CardDesc,
  CompanyTitle, CardTraits, JobTitle, JobTraitList, JobTraitListItem,
  CardTraitElement, CardTraitFeatElement,
  CardDetails, FeatRow, StatusRow, StatusRowList, StatusListItem, StatusListItem1 } from './styles'
import Photosnap from "../../assets/images/photosnap.png";
import { Col } from "react-bootstrap";
import { JobData } from '../../Services/Data/data';

interface Iprops {
  data:JobData
}

const JobCard:React.FC<Iprops> = (props:Iprops) => {
  return (
    <CardRow featured={props.data.features.indexOf('FEATURED') !==-1 }>
      <CardContent>
        <CardLogo src={props.data.logo} />
        <CardDesc>
          <Col className= "col-12">
          <FeatRow>
            <CompanyTitle>{props.data.company_title}</CompanyTitle>
            {props.data.features.length > 0 ? (
              <CardTraits>
                {props.data.features.indexOf('NEW!') !==-1 
                  && 
                  <CardTraitElement>NEW!</CardTraitElement> 
                }
                {props.data.features.indexOf('FEATURED') !==-1 
                  && 
                  <CardTraitFeatElement>FEATURED</CardTraitFeatElement> 
                }   
              </CardTraits>):
            null
            }   
          </FeatRow>
          <FeatRow>
            <JobTitle>{props.data.job_title}</JobTitle>  
            <JobTraitList>
                {props.data.job_tags.map((tag)=>(
                  <JobTraitListItem>{tag}</JobTraitListItem>
                ))}
              </JobTraitList>            
          </FeatRow>
          <StatusRow >
            <CardDetails>
              <StatusRowList>
                {props.data.status.map((status)=>(
                  status.includes('ago') ?
                   <StatusListItem1>{status}</StatusListItem1>:
                   <StatusListItem>{status}</StatusListItem>
                ))}
              </StatusRowList>  
            </CardDetails>
          </StatusRow>
          </Col>          
        </CardDesc>
      </CardContent>
    </CardRow>
  )
}

export default JobCard