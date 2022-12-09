import { Card, Row, Image, Col } from "react-bootstrap";
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
`
export const CompanyTitle = styled.div`
    height:17px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 18px;
    line-height: 17px;
    color: #5CA5A5;
`
export const CardTraits = styled.div`
    display:flex;
    align-items:center;
    width: 138px;
    height: 24px;
    margin-left: 15px;
    margin-right:23px;
`
export const JobTitle = styled.div`
    height: 24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 22px;
    line-height: 24px;
    color: #2B3939;
`
export const CardTraitElement = styled.div`
    background: #5CA5A5;
    border-radius: 12px;
    align-items: center;
    display: flex;
    justify-content: center;
    width:51px;
    height:24px;
    font-family: 'League Spartan';
    font-style: normal;
    font-weight: 700;
    font-size: 14px;
    line-height: 16px;
    text-align: center;
    letter-spacing: -0.107692px;
    text-transform: uppercase;
    color: #FFFFFF;
    padding-left: 2px;
    padding-right: 2px;
    padding-top: 2px;
`
export const CardTraitFeatElement = styled(CardTraitElement)`
    background: #000000;
    width:82px;
    margin-left:14px;
`