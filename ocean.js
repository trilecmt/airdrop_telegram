import { SuiClient, getFullnodeUrl } from "@mysten/sui.js/client";
import { TransactionBlock } from "@mysten/sui.js/transactions";
import { Ed25519Keypair } from "@mysten/sui.js/keypairs/ed25519";
import {
  decodeSuiPrivateKey,
  encodeSuiPrivateKey,
} from '@mysten/sui.js/cryptography';
import { read,utils } from "xlsx";
import fs from 'fs';

const client = new SuiClient({ url: getFullnodeUrl("mainnet") });

function sleep(millis) {
  return new Promise(resolve => setTimeout(resolve, millis));
}

function getKeyPairFromPrivateKey(privateKey){
  const bech32EncodedPrivateKey=privateKey;
  const decodedPrivateKey = decodeSuiPrivateKey(bech32EncodedPrivateKey);
  const encoded = encodeSuiPrivateKey(
    decodedPrivateKey.secretKey,
    'ED25519',
  );
  const { schema, secretKey } = decodeSuiPrivateKey(encoded);
  const keypair = Ed25519Keypair.fromSecretKey(secretKey);

  console.log(keypair.getPublicKey().toSuiAddress());
  return keypair;
}

function getKeyPairFromMnemonic(seedPhrase){
  const keypair= Ed25519Keypair.deriveKeypair(seedPhrase);
  console.log(keypair.getPublicKey().toSuiAddress());
  return keypair;
}

 function getKeyPair(key){
    if(key.startsWith("suiprivkey")){
        return getKeyPairFromPrivateKey(key);
    } 
    else{
      return getKeyPairFromMnemonic(key);
    }
 }

async function getTokenBalance(walletAddress,cointType) {
  const { totalBalance } = await client.getBalance({
    owner: walletAddress,
    coinType: cointType,
  });
  return totalBalance*1e-9;
};


async function claim(key){
  try {
    const keypair=getKeyPair(key)
  const walletAddress=keypair.getPublicKey().toSuiAddress();
  //check balance
  const suiBalance=await getTokenBalance(walletAddress,"0x2::sui::SUI");
  const oceanBalance=await getTokenBalance(walletAddress,"0xa8816d3a6e3136e86bc2873b1f94a15cadc8af2703c075f2d546c2ae367f4df9::ocean::OCEAN");
  console.log(`SUI Balance: ${suiBalance}`)
  console.log(`OCEAN Balance: ${oceanBalance}`)
  if(suiBalance<0.01){
    console.log("Your SUI Balance is very low.")
  }
  const tx = new TransactionBlock();
  tx.moveCall({
    target: `0x2c68443db9e8c813b194010c11040a3ce59f47e4eb97a2ec805371505dad7459::game::claim`,
    arguments: [
      tx.object(
        "0x4846a1f1030deffd9dea59016402d832588cf7e0c27b9e4c1a63d2b5e152873a"
      ),
      tx.object(
        "0x0000000000000000000000000000000000000000000000000000000000000006"
      ),
    ],
  });
  tx.setSender(keypair.getPublicKey().toSuiAddress());
  const result = await client.signAndExecuteTransactionBlock({
    transactionBlock: tx,
    signer: keypair,
    requestType: "WaitForLocalExecution", // or 'WaitForEffectsCert'
    options: {
      showEffects: true,
    },
  });
  sleep(5*1000)
  if(result['confirmedLocalExecution']==true){
     console.log(`${walletAddress} success: , Balance: ${amount}`);
  }
  } catch (error) {
    console.log("Claim failed...")
    console.log(error.message.slice(0, 200));
  }
  
}
  

async function main() {
  const workbook = read(fs.readFileSync('account.xlsx'));
  const worksheet = workbook.Sheets["ocean"];
  // Convert the sheet to JSON
  const walletData = utils.sheet_to_json(worksheet);
  for (let index = 0; index < walletData.length; index++) {
    const element = walletData[index];
    console.log(`${index+1}/${walletData.length} Claiming...`)
    await claim(element['privatekey']); 
    await sleep(1 * 1000);
  }
}

async function run() {
  while (true) {
    try {
      await main();
    } catch (error) {
      console.error('Error:', error);
    }
    console.log("Delay 5m...");
    await sleep(5 * 60 * 1000);
  }
}

run().catch(console.error);
