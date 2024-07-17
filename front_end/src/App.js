import './index.css';

import { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.css';
import { Bar } from 'react-chartjs-2';

// const serverUrl = 'http://0.0.0.0:8000';


const state = {
  labels: ['January', 'February', 'March',
    'April', 'May'],
  datasets: [
    {
      label: 'Rainfall',
      backgroundColor: 'rgba(75,192,192,1)',
      borderColor: 'rgba(0,0,0,1)',
      borderWidth: 2,
      data: [65, 59, 80, 81, 56]
    }
  ]
}

const getData = async() => {
  try {
    const response = await fetch(
      serverUrl + '/getWSB', {
        method: 'get',
        mode: "no-cors"
      }
    )
    const json = await response.json()
    console.log('-'*20)
    console.log(json)
    console.log('-'*20)
    return json
  } catch (error) {
    console.log(error);
    console.log("There seems to be a connection issue, please check server side for errors")
  }
}


class Header extends Component {
  // constructor(props) {
  //   super(props)

  // }

  render() {
    return (
      <nav class="Header">
        Wall Street Bets Sentiment
        <div style={{fontSize:"20px"}}>Created by Andrew Ferruolo</div>
      </nav>
    )
  }
}



class TopTenList extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: this.props.data
    }
    console.log(this.state.data.topTen)
    this.renderTableData = this.renderTableData.bind(this)
  }
  renderTableData() {
    return this.state.data.topTen.map((items) => {
      return (<tr>
        <td>{items}</td>
      </tr>
      )
    })
  }
  render() {

    return (
      <div class="col-md">
        <div id="topTenHeader">
          Top Ten Most Mentioned Stocks:
        </div>
        <table class="topTenTable">
          <th>
            <td class="topTenMember">Ticker</td>
          </th>
          <tbody>

            {this.renderTableData()}
          </tbody>
        </table>
      </div>
    )
  }
}

class GraphFrequency extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: this.props.data
    }
    this.renderGraphData = this.renderGraphData.bind(this);
  }
  renderGraphData(){
  const state = {
    labels: this.state.data.topTen,
      datasets: [
        {
          label: 'Occurance',
          backgroundColor: 'rgba(75,192,192,1)',
          borderColor: 'rgba(0,0,0,1)',
          borderWidth: 2,
          data: this.state.data.occuranceChart
        }
      ]
  }
  return state;
}
render() {
  return (
    <div class="col-md">

      <Bar
        data={this.renderGraphData()}
        options={{
          title: {
            display: true,
            text:'Occurance of each ticker in Daily Discussion',
            fontSize: 20
          },
          legend: {
            display: true,
            position: 'right'
          }
        }}
      />
    </div>
  )
}
}

class Body extends Component {
  constructor(props) {
    super(props);
    this.state = state;
  
  }
  render() {
    console.log(this.state)
    // this.setState(getData)
    return (
      <div class="container">
        <div class="row rowItem">
          <TopTenList data={this.state.data}>
          </TopTenList>
          <GraphFrequency data={this.state.data}>

          </GraphFrequency>

        </div>
      </div>
    )
  }
}

function App() {
  return (
    <div className="mainBody">
      <Header>
      </Header>
      <Body data>
      </Body>
    </div>
  )
}

export default App;
