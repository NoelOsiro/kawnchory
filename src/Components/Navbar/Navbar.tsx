import React from 'react'
import {  NavShape } from './styles'
import Nav from '../../assets/images/nav.jpg'
import FilterBar,{IProps} from '../FilterBar/FilterBar'

const Navbar:React.FC<IProps> = (props:IProps) => {
  return (
    <NavShape>
      <img src={Nav} alt='' />
      <FilterBar change={props.change} clickFilter={props.clickFilter} clear={props.clear}/>
    </NavShape>
  )
}

export default Navbar