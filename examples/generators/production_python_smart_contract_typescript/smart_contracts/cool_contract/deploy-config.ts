import * as algokit from '@algorandfoundation/algokit-utils'
import { CoolContractClient } from '../artifacts/cool_contract/CoolContractClient'

// Below is a showcase of various deployment options you can use in TypeScript Client
export async function deploy() {
  console.log('=== Deploying CoolContract ===')

  const algorand = algokit.AlgorandClient.fromEnvironment()
  const deployer = await algorand.account.fromEnvironment('DEPLOYER')
  
  const appClient = algorand.client.getTypedAppClientByCreatorAndName(CoolContractClient, {
    sender: deployer,
    creatorAddress: deployer.addr,
  })

  const app = await appClient.deploy({
    onSchemaBreak: 'append',
    onUpdate: 'append',
  })

  // If app was just created fund the app account
  if (['create', 'replace'].includes(app.operationPerformed)) {
    await algorand.send.payment({
      amount: algokit.algos(1),
      sender: deployer.addr,
      receiver: app.appAddress,
    })
  }

  const method = 'hello'
  const response = await appClient.hello({ name: 'world' })
  console.log(`Called ${method} on ${app.name} (${app.appId}) with name = world, received: ${response.return}`)
}
