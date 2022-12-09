import React from 'react'
import { CardRow, CardContent, CardLogo, CardDesc, CompanyTitle, CardTraits, JobTitle, CardTraitElement, CardTraitFeatElement} from './styles'
import Photosnap from "../../assets/images/photosnap.png";
import { Row } from 'react-bootstrap';

const JobCard = () => {
  return (
    <CardRow>
        <CardContent>
            <CardLogo src={Photosnap}/>
            <CardDesc>
                <Row style={{display:"flex",alignItems:"center",marginBottom:"10px"}}><CompanyTitle>Photosnap</CompanyTitle>
                <CardTraits>
                  <CardTraitElement>NEW!</CardTraitElement> <CardTraitFeatElement>FEATURED</CardTraitFeatElement></CardTraits></Row>
                <Row style={{display:"flex",marginBottom:"10px"}}><JobTitle>Senior Frontend Developer</JobTitle></Row>
                <Row style={{display:"flex"}}><div>1d ago Featured USA only</div></Row>
                
            </CardDesc>
        </CardContent>
    </CardRow>
  )
}

export default JobCard