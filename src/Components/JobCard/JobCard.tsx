import React from 'react'
import { CardRow, CardContent, 
  CardLogo, CardDesc,
  CompanyTitle, CardTraits, JobTitle, JobTraitList, JobTraitListItem,
  CardTraitElement, CardTraitFeatElement,
  CardDetails, FeatRow, StatusRow, StatusRowList, StatusListItem, StatusListItem1, StatusListItem2 } from './styles'
import Photosnap from "../../assets/images/photosnap.png";
import { Card, Row, Image, Col } from "react-bootstrap";

const JobCard = () => {
  return (
    <CardRow>
      <CardContent>
        <CardLogo src={Photosnap} />
        <CardDesc>
          <Col className= "col-12">
          <FeatRow>
            <CompanyTitle>Photosnap</CompanyTitle>
            <CardTraits>
              <CardTraitElement>NEW!</CardTraitElement>
              <CardTraitFeatElement>FEATURED</CardTraitFeatElement>
              </CardTraits>
          </FeatRow>
          <FeatRow>
            <JobTitle>Senior Frontend Developer</JobTitle>  
            <JobTraitList>
                <JobTraitListItem>Frontend</JobTraitListItem>
                <JobTraitListItem>Senior</JobTraitListItem>
                <JobTraitListItem>HTML</JobTraitListItem>
                <JobTraitListItem>CSS</JobTraitListItem>
                <JobTraitListItem>JavaScript</JobTraitListItem>
              </JobTraitList>            
          </FeatRow>
          <StatusRow >
            <CardDetails>
              <StatusRowList>
                <StatusListItem1>1d ago</StatusListItem1>
                <StatusListItem>Featured</StatusListItem>
                <StatusListItem2>USA only</StatusListItem2>
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