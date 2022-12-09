import { Card, Row, Image,Col } from "react-bootstrap";
import styled from "styled-components";

export const CardRow = styled(Card)`
    width: 1110px;
    height: 152px; 
    background: #FFFFFF;
    box-shadow: 0px 15px 20px -5px rgba(13, 113, 130, 0.15);
    border-radius: 5px;
    border-left: 3px solid  #5CA5A5;
    display: flex;
`
export const CardContent = styled(Row)`
    display: flex;
    width: 1030px;
    height: 89px;
    margin-top:32px;
    margin-bottom:31px;
    margin-left: 40px;
    margin-right:40px;

`
export const CardLogo = styled(Image)`
    border-radius: 50%;
    width: 88px;
    height:88px;
`
export const CardDesc = styled(Col)`
    width: 262px;
    height: 89px; 
    margin-left: 24px;
    border: 2px solid red;
`
export const CompanyTitle= styled.div`
    height:17px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 18px;
    line-height: 17px;
    color: #5CA5A5;
`
export const CardTraits = styled.div`
    width: 138px;
    height: 24px;
    margin-left: 15px;
    margin-right:23px;
    border: 2px solid red;
`
export const JobTitle= styled.div`
    height: 24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 22px;
    line-height: 24px;
    color: #2B3939;
`