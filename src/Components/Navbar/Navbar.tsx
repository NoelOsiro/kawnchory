import React from 'react'
import {  NavShape } from './styles'
import Nav from '../../assets/images/nav.jpg'
import FilterBar from '../FilterBar/FilterBar'

interface IProps {
  change:(e:React.ChangeEvent<HTMLInputElement>)=> void;
}
const Navbar:React.FC<IProps> = (props:IProps) => {
  return (
    <NavShape>
      <img src={Nav} alt='' />
      <FilterBar change={props.change}/>
    </NavShape>
  )
}

export default Navbar