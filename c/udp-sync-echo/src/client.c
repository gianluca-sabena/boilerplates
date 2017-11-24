/*
    Simple udp client
*/
#include<stdio.h> //printf
#include<string.h> //memset
#include<stdlib.h> //exit(0);
#include<arpa/inet.h>
#include<sys/socket.h>
#include <unistd.h>
#include <time.h>
#include <limits.h>

#define SERVER "127.0.0.1"
#define BUFLEN 512  //Max length of buffer
#define PORT 8888   //The port on which to send data

struct stats {
  long items;
  long sum;
  long min;
  long max;
};

void die(char *s) {
  perror(s);
  exit(1);
}

void timer(char *b, struct timespec *ts) {

  if (0 != clock_gettime(_CLOCK_MONOTONIC_RAW, ts))
    printf("Error, can't get clock\n");
  else
    //printf("Time is: %ld \n", ts->tv_nsec);
  memcpy(b,&(ts->tv_nsec),4);
}

void latency(char *b, struct timespec *ts, struct stats *st) {
  long lat =0, tPrev =0;
  if (0 != clock_gettime(_CLOCK_MONOTONIC_RAW, ts))
    printf("Error, can't get clock\n");
  else
    //printf("Time is: %ld \n", ts->tv_nsec);
  memcpy(&tPrev,b,4);
  lat = ts->tv_nsec - tPrev;
  //printf("Latency is: %ld ns \n",lat);
  st->items++;
  st->sum+=lat;
  if(lat>st->max) st->max = lat;
  if(lat<st->min) st->min = lat;
}


int main(void) {
  struct sockaddr_in si_other;
  int s, i, slen = sizeof(si_other);
  char buf[BUFLEN];
  char message[BUFLEN];
  struct timespec tn; // declare struct timespec
  struct stats statLatency = {0,0,INT_MAX,0};

  memset(message, 0, BUFLEN);

  if (0 != clock_getres(_CLOCK_MONOTONIC_RAW, &tn))
    printf("Error, can't get clock precision\n");
  else
    printf("Time resolution: %ld ns \n", tn.tv_nsec);

  if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
    die("socket");
  }

  memset((char *) &si_other, 0, sizeof(si_other));
  si_other.sin_family = AF_INET;
  si_other.sin_port = htons(PORT);

  if (inet_aton(SERVER, &si_other.sin_addr) == 0) {
    fprintf(stderr, "inet_aton() failed\n");
    exit(1);
  }


  for (int j = 0; j < 100; ++j) {
    //printf("Enter message : ");
    //gets(message);
    timer(message,&tn);

    //send the message
    if (sendto(s, message, strlen(message), 0, (struct sockaddr *) &si_other, slen) == -1) {
      die("sendto()");
    }

    //receive a reply and print it
    //clear the buffer by filling null, it might have previously received data
    memset(buf, '\0', BUFLEN);
    //try to receive some data, this is a blocking call
    if (recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *) &si_other, &slen) == -1) {
      die("recvfrom()");
    }
    latency(buf,&tn, &statLatency);


    //puts(buf);
  }

  printf("Latency min: %ld \n",statLatency.min);
  printf("Latency mean: %ld \n",statLatency.sum/statLatency.items);
  printf("Latency max: %ld \n",statLatency.max);

  close(s);
  return 0;
}